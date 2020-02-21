FROM pytorch/pytorch:1.1.0-cuda10.0-cudnn7.5-devel

EXPOSE 6006
EXPOSE 80

RUN apt-get update && apt-get install -y python3 python3-pip libglib2.0-0 libsm6 libxext6 libxrender-dev
RUN python3 -m pip install --upgrade pip

RUN mkdir -p /usr/local/training

COPY /votenet /usr/local/training/votenet
COPY requirements.txt .
RUN pip install -r requirements.txt

ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:$LD_LIBRARY_PATH

WORKDIR /usr/local/training/votenet/pointnet2
RUN python3 setup.py install

WORKDIR /usr/local/training