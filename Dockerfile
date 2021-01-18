FROM python:3.7
COPY . /app
WORKDIR /app
RUN pip install --upgrade pip && pip install -r requirements.txt
EXPOSE 6678
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]