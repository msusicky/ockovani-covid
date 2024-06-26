import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = 'postgresql://__DB_USER__:__DB_PASSWORD__@__DB_HOST__:__DB_PORT__/__DB_NAME__'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TWITTER_CONSUMER_KEY = '__TWITTER_CONSUMER_KEY__'
    TWITTER_CONSUMER_SECRET = '__TWITTER_CONSUMER_SECRET__'
    TWITTER_ACCESS_TOKEN_KEY = '__TWITTER_ACCESS_TOKEN_KEY__'
    TWITTER_ACCESS_TOKEN_SECRET = '__TWITTER_ACCESS_TOKEN_SECRET__'
    CFA_USER = '__CFA_USER__'
    CFA_PASS = '__CFA_PASS__'
    UZIS_TOKEN = '__UZIS_TOKEN__'
