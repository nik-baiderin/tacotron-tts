#FROM nvidia/cuda:10.1-cudnn7-devel-ubuntu18.04
#FROM nvidia/cuda:11.4.2-cudnn8-devel-ubuntu20.04
FROM nvidia/cuda:12.5.1-runtime-ubuntu22.04 AS base
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update --fix-missing && apt-get upgrade -y && apt-get autoremove && apt-get autoclean
RUN apt-get install -y apt-utils ffmpeg python3-pip python3-distutils git nano

ARG PROJECT=sova-tts-gpu
ARG PROJECT_DIR=/sova-tts
RUN mkdir -p $PROJECT_DIR
WORKDIR $PROJECT_DIR

COPY requirements.txt .
COPY librosa-util.py .
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
#RUN git clone https://github.com/sovaai/sova-tts-tps && cd sova-tts-tps && git checkout v1.2.0 && pip3 install .
#RUN cd .. && rm -rf sova-tts-tps
#RUN pip install git+https://github.com/Desklop/StressRNN
RUN pip install git+https://github.com/Den4ikAI/ruaccent.git
#RUN pip install librosa
RUN mv librosa-util.py /usr/local/lib/python3.10/dist-packages/librosa/util/utils.py
RUN apt-get install -y locales && locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

CMD gunicorn --access-logfile - -w 1 --bind 0.0.0.0:8899 app:app --timeout 15000
