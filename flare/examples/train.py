import pandas as pd
from flare.generators import baseline
from sklearn.linear_model import LinearRegression
from joblib import dump

df = pd.read_csv("winequality-red.csv", sep=";")

y = df["quality"]
X = df.copy()
del X["quality"]

# Create Flare Baseline
baseline(X)

# Train Model
model = LinearRegression()
model.fit(X, y)

dump(model, "model.joblib")
