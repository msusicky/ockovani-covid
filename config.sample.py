import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = 'postgresql://<user>:<password>@localhost:5432/<database>'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TWITTER_CONSUMER_KEY = 'SECRET_TOKEN'
    TWITTER_CONSUMER_SECRET = 'SECRET_TOKEN'
    TWITTER_ACCESS_TOKEN_KEY = 'SECRET_TOKEN'
    TWITTER_ACCESS_TOKEN_SECRET = 'SECRET_TOKEN'
    CFA_USER = 'CFA_USER'
    CFA_PASS = 'CFA_PASS'
    UZIS_TOKEN = 'UZIS_TOKEN'
