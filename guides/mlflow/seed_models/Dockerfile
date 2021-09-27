# Don't really need conda but this image is pulled anyway to run MLflow.
# So re-using it is efficient.
FROM continuumio/miniconda3:latest

COPY scikit_elasticnet_wine/requirements.txt /home/scikit_elasticnet_wine/requirements.txt
RUN pip install -r /home/scikit_elasticnet_wine/requirements.txt

COPY . /home

ENTRYPOINT ["/bin/bash", "-c"]

CMD ["./home/wait-for-it.sh -h mlflow -p 5555 -s -t 60 -- python ./home/seed-if-empty.py"]