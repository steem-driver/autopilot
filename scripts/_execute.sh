#!/bin/sh

set -e

pipenv run invoke claim.all-users
