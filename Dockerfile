FROM ubuntu:22.04

RUN apt-get update
RUN apt-get install -y build-essential
RUN apt-get install -y python3 python3-venv
RUN apt-get install -y libpython3-dev libmecab-dev curl git

COPY . /sub
WORKDIR /sub
RUN python3 -m venv .venv
RUN /sub/.venv/bin/pip install -U pip
# RUN ls -al /usr/include | grep python && false
# RUN dpkg -S /usr/include/python3.11/longintrepr.h
#RUN curl https://raw.githubusercontent.com/python/cpython/3.11/Include/cpython/longintrepr.h > /usr/include/python3.11/longintrepr.h
#RUN ls -al /usr/include/python3.11/longintrepr.h
RUN /sub/.venv/bin/pip install -r requirements.txt

ENTRYPOINT ["./.venv/bin/python", "tests.py"]

