#!/usr/bin/env bash

set -e
set -x

rm -rf .pytest_cache
#coverage run --source=app -m pytest app/tests app/tests/login/login_controller.py -x
coverage run --source=app -m pytest app/tests/message/test_message_repository.py -x

coverage report --show-missing
coverage html --title "${@-coverage}"
