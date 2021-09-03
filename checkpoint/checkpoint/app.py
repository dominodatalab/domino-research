from flask import Flask  # type: ignore
from flask import request, Response, send_file  # type: ignore
import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from checkpoint.models import (
    PromoteRequest,
    ModelVersionStage,
    PromoteRequestStatus,
    model_as_dict,
)
from checkpoint.database import db_session
import json
import os

app = Flask(
    __name__,
    static_url_path="/checkpoint/static",
    static_folder="../frontend/build/static",
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


REGISTRY_URL = os.environ.get(
    "CHECKPOINT_REGISTRY_URL", "http://mlflow.gambit-sandbox.domino.tech"
)

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


@app.route("/checkpoint/api/requests")
def list_requests():
    p1 = PromoteRequest(
        title="a request title",
        description="test desc lorem ipsum",
        model_name="some_model",
        model_version="3",
        current_stage=ModelVersionStage.STAGING,
        target_stage=ModelVersionStage.PRODUCTION,
        author_username="josh",
        status=PromoteRequestStatus.OPEN,
    )

    p2 = PromoteRequest(
        title="another request title",
        description="test desc test desc lorem ipsum",
        model_name="some_other_model",
        model_version="2",
        current_stage=ModelVersionStage.STAGING,
        target_stage=ModelVersionStage.PRODUCTION,
        author_username="josh",
        status=PromoteRequestStatus.APPROVED,
    )

    return json.dumps(
        [
            model_as_dict(p1),
            model_as_dict(p2),
        ]
    )


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


if __name__ == "__main__":
    from checkpoint.database import init_db, teardown_db

    init_db()

    p = PromoteRequest(
        title="test",
        description="test desc",
        model_name="some_model",
        model_version="3",
        current_stage=ModelVersionStage.STAGING.value,
        target_stage=ModelVersionStage.PRODUCTION.value,
        author_username="josh",
    )

    db_session.add(p)
    db_session.commit()

    print(PromoteRequest.query.first().current_stage)
    print(json.dumps(p.as_dict()))

    teardown_db()
