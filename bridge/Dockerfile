FROM quay.io/domino/miniconda3:latest

RUN pip install --upgrade pip

WORKDIR /app
COPY setup.py .
COPY bridge bridge
RUN pip install -e .

ENV MIXPANEL_API_KEY=6e8b7ccdef38e1905c270f13f0604111

ENTRYPOINT ["bridge"]
CMD ["run"]
