import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = 'postgresql://ockovani:ockovani@db:5432/ockovani'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TWITTER_CONSUMER_KEY = 'SECRET_TOKEN'
    TWITTER_CONSUMER_SECRET = 'SECRET_TOKEN'
    TWITTER_ACCESS_TOKEN_KEY = 'SECRET_TOKEN'
    TWITTER_ACCESS_TOKEN_SECRET = 'SECRET_TOKEN'
