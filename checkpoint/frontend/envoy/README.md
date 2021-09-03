# Envoy Load Balancer

Configure Envoy to proxy both API and Frontend so that they are both served from the same host:port locally.

## Usage

1. In `config.yaml` on Ubuntu or `config_mac.yaml` on OSX, select either the `api` or `mock` backend cluster for the `/api` route.
1. Start your frontend development server: `npm run dev`.
1. Start your backend, either the mock server or local Skaffold deployment.
1. Run the script in this directory to start Envoy: `run.sh` on Ubuntu and `run_mac.sh` on OSX.

You should now be able to access everything on port 10,000.
