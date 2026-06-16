#!/bin/bash

APP_NAME='start.py'
source ~/.bashrc

# pip3 install -r requirements.txt
/opt/python/python-3.12.11/bin/pip3.12 install --no-index --find-links=whl/ whl/*
/opt/python/python-3.12.11/bin/python3.12 -u start.py