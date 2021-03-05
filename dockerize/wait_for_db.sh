#!/bin/sh

set -e

host="$1"
shift
cmd="$@"

until venv3/bin/python -c "import psycopg2;psycopg2.connect(dbname=\"$POSTGRES_DB\", user=\"$POSTGRES_USER\", host=\"$host\", password=\"$POSTGRES_PASSWORD\")"; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
exec $cmd
