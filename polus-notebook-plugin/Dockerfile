FROM labshare/polyglot-notebook:0.3.2

COPY VERSION /

ARG EXEC_DIR="/opt/executables"

#Copy executable
COPY src ${EXEC_DIR}/

# Install papermill
RUN pip install papermill
RUN pip install git+https://github.com/vatlab/sos-papermill.git

WORKDIR ${EXEC_DIR}

USER root

# Default command. Additional arguments are provided through the command line
ENTRYPOINT ["python", "execute_notebook.py"]