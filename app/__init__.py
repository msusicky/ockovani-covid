import locale
import logging

from flask import Flask, Blueprint
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

from config import Config

app = Flask(__name__)
app.secret_key = '34983459843jf4985435kdsjcf3489fjc3j34c'
app.config.from_object(Config)
mail = Mail(app)

bp = Blueprint('view', __name__, template_folder="templates")

db = SQLAlchemy(app)
migrate = Migrate(app, db)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s')

locale.setlocale(locale.LC_TIME, "cs_CZ")

from app import filters, views, controllers, models, commands

app.register_blueprint(bp)
