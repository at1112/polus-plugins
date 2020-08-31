
FROM labshare/polus-bfio-util:1.3.6-slim-buster

RUN apt-get -y install git

#install conda, create conda env, then install
#need to install:
#bfio
#bioformats
#javabridge


COPY VERSION /
		
ARG EXEC_DIR="/opt/executables"
ARG DATA_DIR="/data"

RUN mkdir -p ${EXEC_DIR} \
    && mkdir -p ${DATA_DIR}/inputs \
    && mkdir ${DATA_DIR}/outputs

COPY src ${EXEC_DIR}/
WORKDIR ${EXEC_DIR}

RUN pip3 install -r ${EXEC_DIR}/requirements.txt --no-cache-dir

ENTRYPOINT ["python3", "main.py"]



#bfio==2.4.2
#python_bioformats==1.5.2
#bioformats==0.1.15