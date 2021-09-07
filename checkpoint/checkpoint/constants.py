ANONYMOUS_USERNAME = "Anonymous"

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
