FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV DEBCONF_NOWARNINGS=yes

RUN apt-get update
RUN apt-get install -y build-essential
RUN apt-get install -y python3 python3-venv
RUN apt-get install -y libpython3-dev libmecab-dev
RUN apt-get install -y git screen redis

COPY . /sub
WORKDIR /sub
RUN python3 -m venv .venv
RUN /sub/.venv/bin/pip install -U pip
RUN /sub/.venv/bin/pip install -r requirements.txt
RUN /sub/.venv/bin/python -m unidic download

COPY ./docker-entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

