FROM jupyter/base-notebook

# Environment manager
RUN mamba install -c conda-forge jupyterlab mamba_gator

# Create kernel tiles for each Conda environment
RUN conda install -c conda-forge nb_conda_kernels

# Install S3FS
USER root
RUN apt-get update && apt-get install -y s3fs
RUN echo "user_allow_other" >> /etc/fuse.conf
USER jovyan

# Install our custom notebook config
COPY config/jupyter_notebook_config.py /home/jovyan/.jupyter/jupyter_notebook_config.py

# Install our custom before-start scripts
COPY start-notebook /usr/local/bin/start-notebook.d/
