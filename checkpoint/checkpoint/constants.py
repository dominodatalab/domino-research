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
    var openRequests = requests.filter(function (request) {
        return request.status == "open";
    }).length;
    element = document.getElementById('requests-count');
    element.innerHTML = openRequests;
    if (openRequests > 0) {
        element.style.display = "inline";
    } else {
        element.style.display = "none";
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
    checkRequests();
    setInterval(checkRequests, 5000);
    setInterval(checkRedirect, 1000);
}
</script>
"""  # noqa: E501

INJECT_ELEMENT = """
<button style="position: fixed; min-width: 165px; width: 10vw; left: 45vw; top: 0px;" type="button" class="ant-btn">
    <a href="/checkpoint/requests">
        🛂 Checkpoint
        <span id="requests-count" style="background-color: red; color: white; margin-left: 10px;" class="ant-tag"></span>
    </a>
</button>
"""  # noqa: E501

INJECT_SCRIPT = INJECT_SCRIPT_TEMPLATE.replace(
    "CHECKPOINT_REDIRECT_PREFIX", CHECKPOINT_REDIRECT_PREFIX
).replace("CHECKPOINT_REDIRECT_SEPARATOR", CHECKPOINT_REDIRECT_SEPARATOR)

GTM_HEAD_SCRIPT = """
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-5QQCHV7');</script>
<!-- End Google Tag Manager -->
"""  # noqa: E501

GTM_BODY_SCRIPT = """
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-5QQCHV7"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
"""  # noqa: E501
