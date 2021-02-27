from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

bp = Blueprint('view', __name__, template_folder="templates")

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import views, models, commands

app.register_blueprint(bp, url_prefix='/ockovani-covid')