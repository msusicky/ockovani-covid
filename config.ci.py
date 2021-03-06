import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = 'postgresql://__DB_USER__:__DB_PASSWORD__@__DB_HOST__:__DB_PORT__/__DB_NAME__'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
