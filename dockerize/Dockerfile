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
ENTRYPOINT ["/ockovani-covid/dockerize/entrypoint.sh"]
