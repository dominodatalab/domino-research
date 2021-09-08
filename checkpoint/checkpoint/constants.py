from checkpoint.types import ModelVersionStage


ANONYMOUS_USERNAME = "Anonymous"

CHECKPOINT_REDIRECT_PREFIX = "checkpoint_redirect"
CHECKPOINT_REDIRECT_SEPARATOR = ":"

NO_VERSION_SENTINAL = "no_version"

STAGES_WITH_CHAMPIONS = {
    ModelVersionStage.STAGING,
    ModelVersionStage.PRODUCTION,
}

INJECT_SCRIPT_TEMPLATE = """
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

// https://stackoverflow.com/a/17076120
function decodeHTMLEntities(text) {
    var entities = [
        ['amp', '&'],
        ['apos', '\\''],
        ['#x27', '\\''],
        ['#x2F', '/'],
        ['#39', '\\''],
        ['#47', '/'],
        ['lt', '<'],
        ['gt', '>'],
        ['nbsp', ' '],
        ['quot', '"']
    ];

    for (var i = 0, max = entities.length; i < max; ++i) {
        text = text.replace(new RegExp('&'+entities[i][0]+';', 'g'), entities[i][1]);
    }

    return text;
}

function checkRedirect() {
    elements = document.getElementsByClassName("ant-message-error");
    if (elements.length > 0) {
        for (i = 0; i< elements.length; i++) {
            const msg = elements[i].children[1].innerHTML;
            if (msg.startsWith("CHECKPOINT_REDIRECT_PREFIX")) {
                elements[i].style.display = "none";
                const parts = msg.split("CHECKPOINT_REDIRECT_SEPARATOR");
                window.location = window.location.protocol + '//' + window.location.host + decodeHTMLEntities(parts[1]);
            }
        }
    }
}

window.onload = function () {
    element = document.getElementsByClassName("header-route-links")[0];
    element.innerHTML += '<a class="header-nav-link header-nav-link-models" href="/checkpoint/requests"><div class="models"><span>Promote Requests</span> <span id="requests-count" class="ant-tag">-</span></div></a>';
    checkRequests();
    setInterval(checkRequests, 5000);
    setInterval(checkRedirect, 1000);
}
</script>
"""  # noqa: E501

INJECT_SCRIPT = INJECT_SCRIPT_TEMPLATE.replace(
    "CHECKPOINT_REDIRECT_PREFIX", CHECKPOINT_REDIRECT_PREFIX
).replace("CHECKPOINT_REDIRECT_SEPARATOR", CHECKPOINT_REDIRECT_SEPARATOR)
