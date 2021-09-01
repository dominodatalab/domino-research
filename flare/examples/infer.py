from flare.alerting import SlackAlertTarget
from flare.runtime import Flare
import pandas as pd
from joblib import load
import logging

logging.basicConfig(level=logging.DEBUG)

# Create alert client
alert = SlackAlertTarget("/XXXXX/XXXXXX/XXXXXXXXXXXXXXXXXXXX")

# Load sample data
x = pd.read_csv("winequality-red.csv", sep=";").head(1)
del x["quality"]

# Load model
model = load("model.joblib")

# Valid Data; No Alerts
with Flare("wine-quality", x, alert):
    output = model.predict(x)


# Insert invalid (below minimum bound) value
x["fixed acidity"] = 3.0

# Generates an error notification
with Flare("wine-quality", x, alert):
    output = model.predict(x)
