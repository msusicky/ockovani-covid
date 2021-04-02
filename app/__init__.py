import locale
import logging

from flask import Flask, Blueprint
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

bp = Blueprint('view', __name__, template_folder="templates")

db = SQLAlchemy(app)
migrate = Migrate(app, db)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s')

locale.setlocale(locale.LC_TIME, "cs_CZ")

from app import filters, views, models, commands

app.register_blueprint(bp)
