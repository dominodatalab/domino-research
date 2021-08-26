FROM quay.io/domino/python-public:3.9.6-slim

RUN pip install --upgrade pip

WORKDIR /app
COPY setup.py .
COPY bridge bridge
RUN pip install -e .

RUN chown -R 1000:1000 /app
USER 1000

ENV MIXPANEL_API_KEY=6e8b7ccdef38e1905c270f13f0604111

ENTRYPOINT ["bridge"]
CMD ["run"]
