FROM python:3.7-slim-buster

ENV BASE_DIR=/usr/local/src/
ENV BASE_USER=demo
ENV PYTHONPATH=${BASE_DIR}

WORKDIR ${BASE_DIR}

RUN useradd -ms /bin/bash -d $BASE_DIR -G sudo ${BASE_USER} && \
  apt-get install -y --fix-broken && apt-get autoremove &&\
  apt-get update && apt-get -y upgrade && apt-get install -y --no-install-recommends apt-utils \
  libssl-dev \
  libpq-dev \
  libffi-dev &&\
  apt-get install -y gcc

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY demo demo 
COPY migrations migrations
COPY run.py boot.sh

RUN chown -R ${BASE_USER}.${BASE_USER} ${BASE_DIR}
USER ${BASE_USER}

EXPOSE 5000
