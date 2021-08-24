FROM quay.io/domino/python-public:3.9.6-slim

ARG MIXPANEL_KEY=""

RUN apt-get update \
    && apt-get install --no-install-recommends -y git \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip

WORKDIR /app
COPY setup.py .
COPY bridge bridge
RUN pip install -e .

RUN chown -R 1000:1000 /app
USER 1000

ENV MIXPANEL_API_KEY=${MIXPANEL_KEY}

ENTRYPOINT ["bridge"]
CMD ["run"]
