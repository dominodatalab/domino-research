FROM continuumio/miniconda3

RUN pip install --upgrade pip

WORKDIR /app
COPY setup.py .
COPY bridge bridge
RUN pip install -e .

RUN chown -R 0:0 /app
USER 0

ENV MIXPANEL_API_KEY=6e8b7ccdef38e1905c270f13f0604111

ENTRYPOINT ["bridge"]
CMD ["run"]
