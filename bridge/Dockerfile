FROM quay.io/domino/python-public:3.9.6-slim

RUN pip install --upgrade pip

WORKDIR /app
COPY setup.py .
COPY bridge bridge
RUN pip install -e .

RUN chown -R 1000:1000 /app
USER 1000

ENTRYPOINT ["bridge"]
CMD ["run"]
