#!/bin/bash
set -eux

screen -S redis -dm redis-server
sleep 3
/sub/.venv/bin/python tests.py

