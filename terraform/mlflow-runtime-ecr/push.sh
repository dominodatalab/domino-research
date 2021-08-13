#!/bin/bash

aws ec2 describe-regions | jq -rc '.[][].RegionName' | while read region
do
        echo ${region}
        aws ecr get-login-password --region ${region} | docker login --username AWS --password-stdin 667552661262.dkr.ecr.${region}.amazonaws.com
        docker tag mlflow-pyfunc:latest 667552661262.dkr.ecr.${region}.amazonaws.com/bridge-mlflow-runtime:latest
        docker push 667552661262.dkr.ecr.${region}.amazonaws.com/bridge-mlflow-runtime:latest
done
