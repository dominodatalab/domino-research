# Local Notebooks

Locally run JupyterLab, with configuration for environment and data sharing,
and real-time collaboration.

# Installation

## 0. Requirements

* `awscli` Version 2
* Docker

## 1. Build Container Image

```bash
docker build -t local-notebooks:latest .
```

## Provision AWS Resources

Select a region, bucket name (must be globally unique), and user name (must be unique in account):

```bash
# us-east-1 is recommended, s3fs has some known issues with other regions
export AWS_REGION=us-east-1
export AWS_BUCKET=<your unique bucket name>
export AWS_USER=local-notebooks
```

Create S3 bucket:

```bash
aws s3 mb ${AWS_BUCKET}
```

Create IAM credentials for bucket access:

```bash
# Create new IAM user
aws iam create-user --user-name ${AWS_USER}
# Create policy for access to S3 bucket created above
aws iam create-policy --policy-name ${AWS_USER} --policy-document "$(envsubst < config/policy.json)"
# Attach policy to user
aws iam attach-user-policy --user-name ${AWS_USER} --policy-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/${AWS_USER}
# Generate API credentials for user
mkdir .aws && aws iam create-access-key --user-name ${AWS_USER} > .aws/credentials
```

## Run Notebook

```bash
docker run --name local-notebook \
    -it -p 8888:8888 \
    -e JUPYTER_ENABLE_LAB=yes \
    -e NB_USER=domino-research \
    --user root \
    --cap-add SYS_ADMIN \
    --security-opt apparmor:unconfined \
    --device /dev/fuse \
    -e AWS_BUCKET=${AWS_BUCKET} \
    -e AWS_REGION=${AWS_REGION} \
    -v $(pwd)/.aws:/etc/aws \
    local-notebooks
```

# Usage

Once the notebook starts, JupyterLab will print out a link to access the UI as usual, use the one with hostname `127.0.0.1` and port `8888`. 

## Shared Data

The S3 bucket is mounted at `/mnt/home`, and set as the default path for the notebook. Any files you store here will be persisted to S3, and can be used by other users with a similar configuration. 

## Environments

Environments are managed through Conda. We have included a number of customizations to make this easy:

- To use an environment, simply select the kernel that corresponds to the environment. We use `nb_conda_kernels` to automatically make all Conda environments available for use in Jupyter as kernels. You will start with only a base environment, but can add as many as you like.

- To create, modify and delete environments, navigate to settings > Conda Packages Manager. From here, you can create, delete and modify environments without touch the command line.

- To use a shared an environment, start this tool pointing at the same S3 bucket as your collaborator. We will automatically load the latest version of all of the Conda environments that are backed up in the S3 bucket and make them available as kernels. Any changes you make or new environments you add will be saved back to the S3 bucket.

Notes and limitations:

- Environments are backed up every minute. Changes you make in the last minute before shut down may not be saved. We suggest waiting a minute before shutting down if you edit the environment.

- Loading shared environments is done synchronously prior to server launch. We are looking into solutions to speed this up by saving the entire environment to S3 rather than only a YAML of the installed packages. We are also looking into making this process asynchronous.

- You can also create and modify environments using the `conda` CLI. But, when you do this, you must add a `--name XXX` to the commands to target a specific environment. If you do `conda install` in a notebook without supplying a name, it will install into the base Conda environment and not the environment you have selected via the kernel.

## Real-Time Collaboration

To start a network tunnel allowing other users to access your local notebook,
open Terminal (inside the Notebook webapp) and launch 
`/usr/local/bin/start-tunnel.d/start-tunnel.sh` script. 
A public URL for your tunnel will appear in the console. For example,

```bash
(base) domino-research@f6d754573428:~$ /usr/local/bin/start-tunnel.d/start-tunnel.sh 
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   159  100   159    0     0    703      0 --:--:-- --:--:-- --:--:--   703
100   631  100   631    0     0   1923      0 --:--:-- --:--:-- --:--:--  1923
100 29.9M  100 29.9M    0     0  25.6M      0  0:00:01  0:00:01 --:--:-- 57.8M
2021-10-27T18:52:57Z INF Thank you for trying Cloudflare Tunnel. Doing so, without a Cloudflare account, is a quick way to experiment and try it out. However, be aware that these account-less Tunnels have no uptime guarantee. If you intend to use Tunnels in production you should use a pre-created named tunnel by following: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps
2021-10-27T18:52:57Z INF Requesting new quick Tunnel on trycloudflare.com...
2021-10-27T18:52:59Z INF +--------------------------------------------------------------------------------------------+
2021-10-27T18:52:59Z INF |  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):  |
2021-10-27T18:52:59Z INF |  https://afghanistan-null-ron-norwegian.trycloudflare.com                                  |
2021-10-27T18:52:59Z INF +--------------------------------------------------------------------------------------------+
2021-10-27T18:52:59Z INF Cannot determine default configuration path. No file [config.yml config.yaml] in [~/.cloudflared ~/.cloudflare-warp ~/cloudflare-warp /etc/cloudflared /usr/local/etc/cloudflared]
2021-10-27T18:52:59Z INF Version 2021.10.5
2021-10-27T18:52:59Z INF GOOS: linux, GOVersion: devel +a84af465cb Mon Aug 9 10:31:00 2021 -0700, GoArch: amd64
2021-10-27T18:52:59Z INF Settings: map[protocol:quic url:http://127.0.0.1:8888]
2021-10-27T18:52:59Z INF cloudflared will not automatically update when run from the shell. To enable auto-updates, run cloudflared as a service: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/run-tunnel/run-as-service
2021-10-27T18:52:59Z INF Generated Connector ID: 1d0fca10-ba61-4620-902a-60ada75c622a
2021-10-27T18:52:59Z INF Initial protocol quic
2021-10-27T18:52:59Z INF Starting metrics server on 127.0.0.1:35577/metrics
<...>
```

Here, `https://afghanistan-null-ron-norwegian.trycloudflare.com` is the URL
that can be shared with your collaborators. Note that the tunnel always uses 
a default port for the given protocol.

