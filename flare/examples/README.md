# Flare Example

This folder contains a small example of Flare's usage.

## Training

In `train.py`, a simple linear regression model is trained
on the wine quality dataset. Before training, Flare's
`baseline` method is invoked using the training dataframe.
This creates our baseline files (`statistics.json` and
`constraints.json`). Finally, the training script saves
the trained model for later use.

## Inference

In `infer.py`, an example of using Flare at inference time
is shown. First, the Slack alert target is configured, as
shown the [quickstart](/flare#2-annotate-your-inference-code).
Next, the model is invoked twice using the Flare context. 
The second invocation purposfully introduces an outlier, which
should trigger a Flare alert. 
