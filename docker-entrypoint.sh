#!/bin/bash
set -eux

screen -S redis -dm redis-server
sleep 3
/venv/bin/python tests.py

