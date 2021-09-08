## Build the frontend
FROM quay.io/domino/node-public:14.16.1-alpine as frontend-builder
WORKDIR /home/node

# Add only the package files and run install to
# make use of docker layer caching
COPY ./frontend/package*.json ./
COPY  ./frontend/packages/ui/package*.json ./packages/ui/

# Run a reproducible install based on the the package-lock.json
# with no modification/updates. Any updates occur via manual
# npm install execution outside of docker.
RUN npm ci

# Add app files to the image
COPY ./frontend /home/node

# Build main and packages/ui (as a dep)
RUN npm run build

## Build the production Python Image
FROM quay.io/domino/python-public:3.9.6-slim

RUN pip install --upgrade pip

WORKDIR /app
COPY setup.py .
COPY checkpoint checkpoint

# Install package
RUN pip install .

# Copy in built frontend
COPY --from=frontend-builder /home/node/build frontend/build

RUN chown -R 1000:1000 /app
USER 1000

ENV FLASK_APP=checkpoint.app
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["gunicorn", "-w 2", "-b 0.0.0.0:5000", "--log-level=info", "--preload", "checkpoint.app:app"]
