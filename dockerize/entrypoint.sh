#!/bin/sh

# run migrations
venv3/bin/flask db upgrade
# fetch data if env var is set
if [ "$FETCH_DATA" = "true" ]; then
    echo "Fetching fresh data"
    venv3/bin/flask fetch-opendata
    venv3/bin/flask compute-metrics
fi
venv3/bin/flask run --host 0.0.0.0 --port 5000
