FROM python:3.7

WORKDIR /ockovani-covid
COPY requirements.txt ./
# install CS locale
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  locales \
  locales-all \
  && rm -rf /var/lib/apt/lists/*
# create virtualenv & install requirements
RUN python3 -m venv venv3 && venv3/bin/pip install --no-cache-dir -r requirements.txt
COPY . .
# NOTE(ivasilev) Commenting out as in docker-compose deployment the startup will be performed after making
# sure the db is fully up and running. Not removing completely in case someone needs to run it via plain
# docker/podman (uncommenting is easier than writing from scratch)
#ENTRYPOINT ["/ockovani-covid/dockerize/entrypoint.sh"]
