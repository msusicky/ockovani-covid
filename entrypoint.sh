#!/bin/sh
venv3/bin/flask db upgrade
venv3/bin/flask run --host 0.0.0.0
