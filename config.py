from flask import Flask, g

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SEND_FILE_MAX_AGE_DEFAULT = 300

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class myConfig:
    FLASK_APP = 'app.py'
    FLASK_DEBUG = 1
    SQLALCHEMY_DATABASE_URI = 'postgresql://ockovani:foaeiwfjewfoij@localhost:5432/ockovani'
