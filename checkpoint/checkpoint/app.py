from checkpoint.models import PromoteRequest, PromoteRequestStatus
from checkpoint.database import db_session
from checkpoint.registries import MlflowRegistry, RegistryException
from checkpoint.types import ModelVersion, ModelVersionStage
from flask import Flask  # type: ignore
from flask import request, Response, send_file, jsonify  # type: ignore
from sqlalchemy.exc import IntegrityError, StatementError  # type: ignore

from bs4 import BeautifulSoup  # type: ignore
import requests  # type: ignore
from typing import Dict
import logging
import os
from dataclasses import asdict


logger = logging.getLogger(__name__)

app = Flask(
    __name__,
    static_url_path="/checkpoint/static",
    static_folder="../frontend/build/static",
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

if app.debug:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.WARNING)


@app.before_first_request
def initialize_db():
    from checkpoint.database import init_db

    init_db()
    app.logger.info("Initialized DB")


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
    app.logger.debug("Shutdown DB Session")


REGISTRY_URL = os.environ.get(
    "CHECKPOINT_REGISTRY_URL", "http://mlflow.gambit-sandbox.domino.tech"
)

mlflow_registry = MlflowRegistry(REGISTRY_URL, REGISTRY_URL)

INJECT_SCRIPT = """
<script>
function checkRequests () {
    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var requests = JSON.parse(this.responseText);
            setRequests(requests);
        }
    };
    req.open("GET", "/checkpoint/api/requests", true);
    req.send();
}

function setRequests(requests) {
    element = document.getElementById('requests-count');
    element.innerHTML = requests.length;
    if (requests.length === 0) {
        element.classList.remove('ant-tag-red');
    } else {
        element.classList.add('ant-tag-red');
    }
}

function checkRedirect() {
    elements = document.getElementsByClassName("ant-message-error");
    if (elements.length > 0) {
        for (i = 0; i< elements.length; i++) {
            if (elements[i].children[1].innerHTML == "Redirecting to Checkpoint") {
                window.location = window.location.protocol + '//' + window.location.host + '/checkpoint/requests/new';
            }
        }
    }
}

window.onload = function () {
    element = document.getElementsByClassName("header-route-links")[0];
    element.innerHTML += '<a class="header-nav-link header-nav-link-models" href="/checkpoint/requests"><div class="models"><span id="requests-count" class="ant-tag">-</span><span>Promote Requests</span></div></a>';
    checkRequests();
    setInterval(checkRequests, 5000);
    setInterval(checkRedirect, 1000);
}
</script>
"""  # noqa: E501


@app.route(
    "/ajax-api/2.0/preview/mlflow/model-versions/transition-stage",
    methods=["POST"],
)
def intercept_tag():
    return "Redirecting to Checkpoint"


@app.route(
    "/checkpoint/api/requests",
    methods=["POST"],
)
def create_request():

    promote_request_data = request.json

    app.logger.info(
        "Received request to create PromoteRequest with data: "
        + f"{promote_request_data}"
    )

    if promote_request_data is None:
        app.logger.error("No POST body in create request")

    try:
        p = PromoteRequest(**promote_request_data)
        db_session.add(p)
        db_session.commit()
        return Response("Created", 201)

    # TypeError is insufficient/extra parameters throws at instantiation
    # IntegrityError is missing/null value error from the DB
    # StatementError is an invalid enum value from the DB
    except (TypeError, StatementError, IntegrityError) as e:
        app.logger.error(e)
        db_session.rollback()
        return Response(f"Invalid body: {promote_request_data}", 400)


@app.route(
    "/checkpoint/api/requests",
    methods=["GET"],
)
def list_requests():
    return jsonify([p.as_dict() for p in PromoteRequest.query.all()])


@app.route(
    "/checkpoint/api/requests/<id>",
    methods=["PUT"],
)
def update_request(id: int):
    promote_request = PromoteRequest.query.get(id)

    update_fields_and_values: Dict[str, str] = request.json  # type: ignore
    update_field_names = set(update_fields_and_values.keys())
    target_status = update_fields_and_values["status"]

    updates_status_field = "status" in update_field_names
    updates_to_valid_status = (
        target_status in PromoteRequest.VALID_STATUS_UPDATE_VALUES
    )
    updates_from_valid_status = (
        promote_request.status == PromoteRequestStatus.OPEN.value
    )
    updates_only_review_fields = update_field_names.issubset(
        PromoteRequest.UPDATEABLE_FIELDS
    )

    if not updates_status_field:
        return Response("Must update the 'status' field", 400)

    elif not updates_from_valid_status:
        return Response(
            "Cannot review request that is not open",
            400,
        )

    elif not updates_to_valid_status:
        return Response(
            f"Status value '{target_status}' must be "
            + f"in {PromoteRequest.VALID_STATUS_UPDATE_VALUES}",
            400,
        )

    elif not updates_only_review_fields:
        return Response(
            f"Can only update {PromoteRequest.UPDATEABLE_FIELDS}", 400
        )

    for field, val in update_fields_and_values.items():
        setattr(promote_request, field, val)

    try:
        # detect any schema violations etc
        db_session.flush()

        # update mlflow
        app.logger.info(
            f"Updating model {promote_request.model_name} "
            + f"version {promote_request.model_version} "
            + f"to stage: {promote_request.target_stage}"
        )

        if promote_request.status == PromoteRequestStatus.APPROVED.value:
            mlflow_registry.transition_model_version(
                ModelVersion(
                    model_name=promote_request.model_name,
                    id=promote_request.model_version,
                ),
                ModelVersionStage(promote_request.target_stage),
            )

        # Now that MLFlow is updated, commit.
        db_session.commit()

        return promote_request.as_dict()

    # ValueError from invalid enum value
    # StatementError from invalid enum at DB
    # IntegrityError from invalid missing value at DB
    except (ValueError, StatementError, IntegrityError) as e:
        app.logger.error(e)
        db_session.rollback()
        return Response(f"Invalid body: {update_fields_and_values}", 400)
    except RegistryException as e:
        app.logger.error("Cause: ", e.cause)
        db_session.rollback()
        return Response(f"Registry update failed: {e.cause}", 500)


@app.route("/checkpoint/api/models/<model_name>/versions")
def list_model_versions(model_name):
    models_versions = mlflow_registry.list_model_versions(
        model_name=model_name
    )
    return jsonify([asdict(v) for v in models_versions])


@app.route("/checkpoint/api/models")
def list_models():
    models = mlflow_registry.list_models()
    return jsonify([asdict(m) for m in models])


@app.route("/checkpoint/<path:path>")
def spa_index(path):
    return send_file("../frontend/build/index.html")


@app.route(
    "/",
    defaults={"path": ""},
    methods=["GET", "POST", "PUT", "HEAD", "DELETE"],
)
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "HEAD", "DELETE"])
def proxy(path):
    resp = requests.request(
        method=request.method,
        url=f"{REGISTRY_URL}/{path}",
        headers={
            key: value for (key, value) in request.headers if key != "Host"
        },
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
        params=dict(request.args),
    )

    excluded_headers = [
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
    ]
    headers = [
        (name, value)
        for (name, value) in resp.raw.headers.items()
        if name.lower() not in excluded_headers
    ]

    if resp.content.startswith(bytes("<!doctype html>", "utf-8")):
        soup = BeautifulSoup(resp.content.decode("utf-8"), "html.parser")
        print(soup.body.append(BeautifulSoup(INJECT_SCRIPT)))
        content = str(soup).encode("utf-8")
    else:
        content = resp.content

    response = Response(content, resp.status_code, headers)
    return response
