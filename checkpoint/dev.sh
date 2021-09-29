#!/bin/bash

pip install -U flask-cors

CHECKPOINT_ANALYTICS_OPT_OUT=1 FLASK_APP=checkpoint.app FLASK_ENV=development CHECKPOINT_REGISTRY_URL=http://localhost:5555 flask run
