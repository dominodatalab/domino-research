FROM jupyter/base-notebook

# Environment manager
RUN mamba install -c conda-forge jupyterlab mamba_gator nb_conda_kernels

# Install S3FS
USER root
RUN apt-get update && apt-get install -y git s3fs jq && rm -rf /var/lib/apt/lists/*
RUN echo "user_allow_other" >> /etc/fuse.conf
USER jovyan

# Install git extension and cell execution timer
RUN pip install --upgrade jupyterlab-git jupyterlab_execute_time

# Install our custom notebook config
COPY config/jupyter_notebook_config.py /home/jovyan/.jupyter/jupyter_notebook_config.py

# Override settings
COPY config/overrides.json /opt/conda/share/jupyter/lab/settings/overrides.json

# Install our custom before-start scripts
COPY config/start-notebook /usr/local/bin/start-notebook.d/
