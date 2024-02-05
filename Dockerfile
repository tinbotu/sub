FROM python:2.7.18-buster
# FROM python:3.12-slim

RUN apt-get update
RUN apt-get install -y libmecab-dev

COPY . /sub
WORKDIR /sub
RUN virtualenv --python=$(which python2) .venv
# RUN python -m venv .venv
RUN /sub/.venv/bin/pip install -U pip
RUN /sub/.venv/bin/pip install -r requirements.txt

ENTRYPOINT ["./.venv/bin/python", "tests.py"]

