# TODO Project Title

New project checklist:

- [ ] Set project title in this README.
- [ ] Set Google Tag Manager Id in `public/index.html` (two locations, `TODO_GTM`)
- [ ] Set page title in `public/index.html` (`TODO_TITLE`))
- [ ] Set Intercom App Id in `public/index.html` (`TODO_INTERCOM`)
- [ ] Add TS client as dependency for both SPA and component package.
- [ ] Update favicons and web manifest in `public` directory.
- [ ] CircleCI
  - Create new CircleCI project
  - Create ECR repository for built images
  - Set `ECR_REGISTRY` and `ECR_REPOSITORY` variables in CircleCI project.
  - Configure AWS credentials for CircleCI and set environment variables in CircleCI project.
- [ ] Set up Chromatic project for new repository.

## Todo

- [ ] Basic navigation and layout
- [ ] Vercel or other branch SPA deployment
- [ ] Documentation (below)

## Installation

After a fresh clone, these are the steps you need to run in order to get a working setup:

```
[install node/npm???]
npm install
npm run dev
```

After this completes (it'll take a few minutes the very first time), then you will be able to access your React dev server
at http://localhost:3000.

## Local Development

### MLflow

Follow the [MLflow guide](/guides/mlflow) to set up MLflow running on `localhost:5555`.

### API

Launch the Python API on `localhost:5000` in development mode by running in the `/checkpoint` directory:

```bash
pip install -e .
./dev.sh
```

### Frontend

Start the Frontend in development mode:

```bash
npm run dev
```

Finally, navigate to [http://localhost:3000/checkpoint/requests](http://localhost:3000/checkpoint/requests).
