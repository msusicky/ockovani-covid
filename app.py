import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from sqlalchemy.orm import sessionmaker

from models import db
from views import *

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

some_engine = create_engine('postgresql://ockovani:ockovani2021@localhost:5432/ockovani')
Session = sessionmaker(bind=some_engine)
app.session = Session()
app.logger.info('Connection set up')


def create_app(config):
    """Construct the core application."""
    app.config.from_object(config)
    db.init_app(app)
    with app.app_context():
        a = 0
    app.logger.info(app.config['SQLALCHEMY_DATABASE_URI'])
    app.session = db.session
    return app


def register_blueprints(app):
    app.register_blueprint(my_view)


if __name__ == '__main__':
    app = create_app('config.myConfig')
    handler = RotatingFileHandler('ockovani.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.DEBUG)

    # Logging of SQL queries
    # logging.basicConfig()
    # logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    app.logger.addHandler(handler)
    # app.logger.setLevel(logging.DEBUG)
    register_blueprints(app)

    app.run(debug=False, threaded=True, port=5000, host='0.0.0.0')
