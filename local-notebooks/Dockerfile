FROM jupyter/base-notebook

# Environment manager
RUN mamba install -c conda-forge jupyterlab mamba_gator nb_conda_kernels

# Install git extension and cell execution timer
RUN pip install --upgrade jupyterlab-git jupyterlab_execute_time

# Install S3FS and other deps
USER root
RUN apt-get update && apt-get install -y git s3fs jq cron && rm -rf /var/lib/apt/lists/*

# Configure S3FS
RUN echo "user_allow_other" >> /etc/fuse.conf

# Configure cron
COPY config/cron /usr/local/sbin/dom_cron/
RUN crontab /usr/local/sbin/dom_cron/root
RUN chmod +x /usr/local/sbin/dom_cron/dump_conda.sh

USER jovyan

# Install our custom notebook config
COPY config/jupyter_lab_config.py /home/jovyan/.jupyter/jupyter_lab_config.py

# Override settings
COPY config/overrides.json /opt/conda/share/jupyter/lab/settings/overrides.json

# Install our custom before-start scripts
COPY config/start-notebook /usr/local/bin/start-notebook.d/
COPY config/before-notebook /usr/local/bin/before-notebook.d/

# Install the script for launching a tunnel.
COPY --chmod=0755 config/start-tunnel /usr/local/bin/start-tunnel.d/


