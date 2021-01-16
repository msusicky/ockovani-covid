from flask import Blueprint, render_template, g, session, redirect, url_for, request
from sqlalchemy import *
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from markupsafe import escape
import requests

from app import app
from models import OckovaciMisto

my_view = Blueprint('my_view', __name__, template_folder="templates")

@my_view.route('/')
def index():
    app.logger.info('index')
    all_data = None
    return render_template('index.html', data=all_data)

#@my_view.route("/ockovaci_mista/<mesto>")
#def ockovaci_mista(mesto):
    """
    It lists only specified abstract roles.
    :param ar_id:
    :return:
    """
#    nactene_informace = app.session.query(OckovaciMista).from_statement(text("SELECT ... FROM ... where ar_id=:mesto_param")).params(mesto_param=mesto).all()
#    return render_template('abstract_komponent_roles.html', data=nactene_informace)

@my_view.route("/info")
def info():
    ockovani_info=app.session.query(OckovaciMisto).from_statement(text("select * from ockovaci_misto")).all()

    #my small test of API
    url = 'https://reservatic.com/public_services/411747/public_operations/5971/hours?date=2021-4-09'
    data = ''
    response = requests.get(url, data=data, headers={"Content-Type": "application/json"})
    #v response mam volne terminy :)
    print(response)

    return render_template('ockovani_info.html', data=ockovani_info, volne_terminy=response.text)
