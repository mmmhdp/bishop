#!/usr/bin/env bash

set -e
set -x

rm -rf .pytest_cache
coverage run --source=app -m pytest app/tests -x

coverage report --show-missing
coverage html --title "${@-coverage}"
