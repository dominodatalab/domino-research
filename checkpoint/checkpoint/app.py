from checkpoint.types import ModelVersionStage, Model, ModelVersion
from checkpoint.models import PromoteRequest, PromoteRequestStatus
from checkpoint.database import db_session
from checkpoint.registries import MlflowRegistry, RegistryException
from checkpoint.constants import (
    INJECT_SCRIPT,
    ANONYMOUS_USERNAME,
    CHECKPOINT_REDIRECT_PREFIX,
    CHECKPOINT_REDIRECT_SEPARATOR,
)
from checkpoint.views import (
    PromoteRequestDetailsView,
    PromoteRequestView,
    VersionDetailsView,
)
from flask import Flask  # type: ignore
from flask import request, Response, send_file, jsonify  # type: ignore
from sqlalchemy.exc import IntegrityError, StatementError  # type: ignore

from bs4 import BeautifulSoup  # type: ignore
import requests  # type: ignore
from typing import Dict, Any, Optional
import logging
import os
from dataclasses import asdict
import urllib.parse
from datetime import datetime

logger = logging.getLogger(__name__)

app = Flask(
    __name__,
    static_url_path="/checkpoint/static",
    static_folder="../frontend/build/static",
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# If running in debug, log at debug
if app.debug:
    logger.setLevel(logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)

# If running through gunicorn, inherit log level.
else:
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    logger.setLevel(gunicorn_logger.level)


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

registry = MlflowRegistry(REGISTRY_URL, REGISTRY_URL)


@app.route(
    "/ajax-api/2.0/preview/mlflow/model-versions/transition-stage",
    methods=["POST"],
)
def intercept_tag():
    create_params = {
        "model": request.json["name"],
        "version": request.json["version"],
        "target": request.json["stage"],
    }

    encoded_params = urllib.parse.urlencode(create_params)
    new_pr_path = f"/checkpoint/requests/new?{encoded_params}"

    return (
        CHECKPOINT_REDIRECT_PREFIX
        + CHECKPOINT_REDIRECT_SEPARATOR
        + new_pr_path
    )


@app.route(
    "/checkpoint/api/requests",
    methods=["POST"],
)
def create_request():

    promote_request_data = request.json

    if promote_request_data is None:
        e = ValueError("No JSON POST body in create request")
        app.logger.error(e)
        raise e

    internal_stage = registry.checkpoint_stage_for_registry_stage(
        promote_request_data["target_stage"]
    )
    promote_request_data["target_stage"] = internal_stage

    # TODO: capture from oauth header if present
    promote_request_data["author_username"] = ANONYMOUS_USERNAME

    promote_request_data["status"] = PromoteRequestStatus.OPEN
    promote_request_data["created_at"] = datetime.utcnow()

    app.logger.info(
        "Create PromoteRequest with data: " + f"{promote_request_data}"
    )

    try:
        p = PromoteRequest(**promote_request_data)
        db_session.add(p)
        db_session.commit()

        return asdict(_to_promote_request_view(p))

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
    return jsonify(
        [
            asdict(_to_promote_request_view(p))
            for p in PromoteRequest.query.all()
        ]
    )


@app.route(
    "/checkpoint/api/requests/<id>",
    methods=["PUT"],
)
def update_request(id: int):
    promote_request = PromoteRequest.query.get(id)

    update_fields_and_values: Dict[str, Any] = request.json  # type: ignore
    update_field_names = set(update_fields_and_values.keys())
    target_status = update_fields_and_values["status"]

    updates_status_field = "status" in update_field_names
    updates_to_valid_status = (
        target_status in PromoteRequest.VALID_STATUS_UPDATE_VALUES
    )
    updates_from_valid_status = (
        promote_request.status == PromoteRequestStatus.OPEN
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

    # TODO: capture from oauth header
    update_fields_and_values["reviewer_username"] = ANONYMOUS_USERNAME

    update_fields_and_values["closed_at"] = datetime.utcnow()

    update_fields_and_values["status"] = PromoteRequestStatus(
        update_fields_and_values["status"]
    )

    for field, val in update_fields_and_values.items():
        setattr(promote_request, field, val)

    try:
        # detect any schema violations etc
        db_session.flush()

        # update mlflow
        app.logger.info(
            f"Updating model {promote_request.model_name} "
            + f"version {promote_request.version_id} "
            + f"to stage: {promote_request.target_stage}"
        )

        if promote_request.status == PromoteRequestStatus.APPROVED:
            registry.transition_model_version_stage(
                ModelVersion(
                    model_name=promote_request.model_name,
                    id=promote_request.version_id,
                ),
                promote_request.target_stage,
            )

        # Now that MLFlow is updated, commit.
        db_session.commit()

        return asdict(_to_promote_request_view(promote_request))

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


@app.route(
    "/checkpoint/api/requests/<id>/details",
    methods=["GET"],
)
def view_request_details(id):
    promote_request = PromoteRequest.query.get(id)

    champion_version = registry.get_model_version_for_stage(
        Model(promote_request.model_name),
        promote_request.target_stage,
    )

    challenger_version = ModelVersion(
        promote_request.version_id, promote_request.model_name
    )

    details_view = PromoteRequestDetailsView(
        promote_request.id,
        champion_version_details=_to_version_details_view(
            champion_version, stage=promote_request.target_stage
        )
        if champion_version
        else None,
        challenger_version_details=_to_version_details_view(
            challenger_version
        ),
    )

    return asdict(details_view)


@app.route("/checkpoint/api/stages")
def list_stages():
    stage_names = registry.list_stages_names()
    return jsonify(stage_names)


@app.route("/checkpoint/api/models/<model_name>/versions")
def list_model_versions(model_name):
    models_versions = registry.list_model_versions(model_name=model_name)
    return jsonify([asdict(v) for v in models_versions])


@app.route("/checkpoint/api/models")
def list_models():
    models = registry.list_models()
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


def _to_promote_request_view(
    promote_request: PromoteRequest,
) -> PromoteRequestView:

    external_target_stage = registry.registry_stage_for_checkpoint_stage(
        promote_request.target_stage
    )
    return PromoteRequestView(
        id=promote_request.id,
        status=promote_request.status.value,
        title=promote_request.title,
        description=promote_request.description,
        created_at_epoch=promote_request.created_at.timestamp(),
        closed_at_epoch=promote_request.closed_at.timestamp()
        if promote_request.closed_at
        else None,
        model_name=promote_request.model_name,
        version_id=promote_request.version_id,
        target_stage=external_target_stage,
        author_username=promote_request.author_username,
        reviewer_username=promote_request.reviewer_username,
        review_comment=promote_request.review_comment,
    )


def _to_version_details_view(
    version: ModelVersion, stage: Optional[ModelVersionStage] = None
) -> VersionDetailsView:
    if stage is None:
        stage = registry.get_stage_for_model_version(version)

    external_stage = registry.registry_stage_for_checkpoint_stage(stage)

    version_data = registry.get_model_version_details(version)

    return VersionDetailsView(
        id=version.id,
        stage=external_stage,
        metrics=version_data.metrics if version_data else {},
        parameters=version_data.parameters if version_data else {},
        tags=version_data.tags if version_data else {},
    )
