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
cd packages/ui
npm install
npm run build
cd ../../  # back to root of the repo
npm install
npm run dev
```

After this completes (it'll take a few minutes the very first time), then you will be able to access your React dev server
at http://localhost:3000.

## Local Development

### Mock API
### Local API
### Staging API

## Branch Deployments

## Storybook
