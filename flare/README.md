# :sparkler: Flare

Monitor models and get alerts without capturing/exfiltrating production inference data.

![build](https://github.com/dominodatalab/domino-research/actions/workflows/flare.yml/badge.svg?branch=main)
[![PyPI version](https://badge.fury.io/py/domino-flare.svg)](https://badge.fury.io/py/domino-flare)

## Why

Flare is a lightweight monitoring framework that runs alongside your inference code.
It requires no additional infrastructure and does not capture/exfiltrate production data.

- Model authors generate constraints and statistics locally using
  the model's training data. These are stored and packaged alongside the model inference code.
  When constraint violation / outliers are detected, alerts are sent through Slack/Zapier
  or to any other webhook target.

- ML/DevOps Engineers host or execute the model using whatever tool/runtime they prefer.
  There is no need to build bespoke, scalable, and secure data pipelines to capture and
  analyze production inference traffic for each model.

## Quick Start

### 0. Install Flare in your Training Environment

First, Flare should be installed in your training environment (or wherever
it is that you work with your training data).

```
pip install domino-flare
```

### 1. Generate constraints and statistics

Flare runs two kinds of checks at inference-time. `Constraints`
validate the presence, type, and unique values of incoming data.
`Statistics` refer to statistical properties of the training data
and are currently used to detect bounds/outliers. We plan to support
data drift detection in an upcoming release.

Flare automatically generates constraints and statistics from a Pandas DataFrame
containing your training data. To do this, run the code below in your training
notebook/script (you can replace the example DataFrame with your real training
data):

```python
from flare.generators import baseline as flare_baseline
from flare.examples import generate_example_dataframe

X = generate_example_dataframe()
flare_baseline(X)
```

This will create two files in your working directory - `constraints.json` and `statistics.json`.
You can explore these in your text editor of choice or explore the notebook
[here](https://github.com/dominodatalab/domino-research/blob/main/flare/examples/gen_constraints.ipynb)
for a deeper dive into how we generate the values and the structure of the JSON objects.

*Note*: Flare uses the same format that AWS SageMaker Monitoring uses for these files. This means
that if you have already used AWS Sagemaker's baselining functonality, we can ingest the baselines
in JSON format. Unlike SageMaker monitoring, Flare DOES NOT require storing your production data,
which means it is cheaper to run and preserves the security of production data.

### 2. Annotate your inference code

Each time your model is executed for inference, Flare will analyze the incoming features
and through an alert if constraints/statistics are violated. It will also capture and report
any exceptions that occur within the context. This functionality requires configuring an alert target and then
executing your inference code inside a Flare context.

*Notes:*

- Flare expects to find the `constraints.json` and `statistics.json` in the working
  directory of your inference script. You can change the location Flare will look for these
  files by setting the environment variables `FLARE_STATISTICS_PATH_VAR` and `FLARE_CONSTRAINTS_PATH_VAR`.


- Flare needs to be installed in your inference environment. Don't forget to add `domino-flare` to your
  `requirements.txt`, `conda.yaml`, `Dockerfile` or other environment management solution.

#### Configure an Alert Target

Flare supports three alert targets: Slack, Zapier, and Custom Webhooks. Zapier is a great way
to integrate Flare with an enormous variety of other services.

**Slack**

To configure Slack Alerts follow the steps below. This assumes you have
access to a Slack Workspace:

1. Navigate to https://api.slack.com/apps
2. Create app > from manifest
3. Select your desired Slack Workspace
4. Paste the manifest below
5. Click the "Install in Workspace" button and follow the flow
   to select the Slack channel alerts will be sent to.
6. Navigate to "Incoming Webhooks" in the left menu and copy the part of your
   unique URL after `https://hooks.slack.com/services`. The format
   will be: `/XXXXX/XXXXXX/XXXXXXXXXXXXXXXXXXXX` with a leading slash.

```
_metadata:
  major_version: 1
  minor_version: 1
display_information:
  name: Flare Alerts
features:
  bot_user:
    display_name: Flare Alerts
    always_online: false
oauth_config:
  scopes:
    bot:
      - incoming-webhook
settings:
  org_deploy_enabled: false
  socket_mode_enabled: false
  token_rotation_enabled: false
```

When you have the URL path, paste the following into your inference code:

```python
from flare.alerting import SlackAlertTarget
alert_target = SlackAlertTarget("/XXXXX/XXXXXX/XXXXXXXXXXXXXXXXXXXX")
```

**Zapier**

Configure a Zap that connects the "Webhooks by Zapier" service to
a service of your choice. Select the "Catch Hook" type when asked.

Copy the URL and use the part after `https://hooks.zapier.com/hooks/catch`:

```python
from flare.alerting import ZapierAlertTarget
alert_target = ZapierAlertTarget("/XXXXX/XXXXXX")
```

This is an example of the Payload that will be sent to the webhook on an alert:

```JSON
{
  "model_name": "wine-quality",
  "features": [
    {
      "name": "fixed acidity",
      "kind": "Bound"
    }
  ],
  "exception": null
}
```

**Custom Webhook**

You can send a webhook to any URL that accepts POST requests. The alert payload
will be JSON formatted (see the example above):

```python
from flare.alerting import CustomAlertTarget
alert_target = CustomAlertTarget("https://yourserver.com/incoming/hooks")
```

#### Configure the Flare Context

Once you have configure your alert target, add the following to your
inference code. Note that we expect your inference data to be formatted
as a Pandas DataFrame. This should work for most modeling frameworks
that follow the Scikit Learn predict API.

When you create the context, you supply a unique model name,
your input features, and the alert target configured above.

```
X = ... # Example input features from your API/DB read etc
model = load("model.joblib") # your model

# This is the Flare context. 
with Flare("wine-quality", X, alert_target):
    
    # Your normal inference code goes here
    output = model.predict(X)
```

### 3. Try it out

That's it! Try triggering a test alert by sending some data that violates your constraint.

If you don't want to deploy your own model, try our example code by doing the following:

1. Clone this repo `git clone https://github.com/dominodatalab/domino-research.git`
2. Install the required packages `pip install scikit-learn pandas domino-flare`
3. `cd domino-research/flare/examples`
4. Run `python train.py`
5. Edit `infer.py` to add your Slack webhook path from the step above.
5. Run `python infer.py`. You should get an alert in your Slack channel.

## Analytics

Flare collects *completely anonymous* usage metrics by default.

We collect the following metrics:

- Count of Baselines generated. Collected when you run `flare.generators.baseline(...)`.

We do not collect any of your data or the constraints/statistics generated based on your data.

To opt out, set the environment variable `FLARE_ANALYTICS_OPT_OUT=1` before importing flare.
You can do this by adding `os.environ["FLARE_ANALYTICS_OPT_OUT"] = "1"` in your python code:

```python
import os
os.environ["FLARE_ANALYTICS_OPT_OUT"] = "1"
# ...
from flare.generators import baseline
df = pd.DataFrame(...)
baseline(df)
```

## Development

#### 1. In this directory (`domino-research/flare`): 

```bash
# Install as local package
pip install -e .
```

## Linting / Testing

To run our linting/testing:

```
pip install -r requirements-dev.txt

# Type check
mypy flare

# Lint
flake8 flare

python -m pytest

# Automatically fix lints
black .
```

We also have these set up as pre-commit hooks. To use pre-commit:

```
pip install -r requirements-dev.txt

# install pre-commit
pre-commit install
```

The checks above will run on each git commit.
