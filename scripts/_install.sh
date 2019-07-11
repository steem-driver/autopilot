#!/bin/sh

set -e

pip install pipenv
pipenv install --pypi-mirror https://pypi.python.org/simple
