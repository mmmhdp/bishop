#!/usr/bin/env bash

set -e
set -x

#coverage run --source=app -m pytest
coverage run --source=app/tests/user -m pytest app/tests/user -x
#coverage run --source=app/tests/avatar -m pytest app/tests/avatar -x
coverage report --show-missing
coverage html --title "${@-coverage}"
