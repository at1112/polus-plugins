
FROM labshare/polus-bfio-util:2.4.4-imagej

RUN apt-get -y install git

COPY VERSION /
		
ARG EXEC_DIR="/opt/executables"
ARG DATA_DIR="/data"

RUN mkdir -p ${EXEC_DIR} \
    && mkdir -p ${DATA_DIR}/inputs \
    && mkdir ${DATA_DIR}/outputs

COPY src ${EXEC_DIR}/
WORKDIR ${EXEC_DIR}

RUN pip3 install bfio
RUN pip3 install bioformats
RUN pip install javabridge
RUN pip3 install cython
RUN pip3 install pyjnius==1.2.0
RUN pip3 install -r ${EXEC_DIR}/requirements.txt --no-cache-dir

ENTRYPOINT ["python3", "main.py"]
