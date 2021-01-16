from flask import Blueprint, render_template, g, session, redirect, url_for, request
from sqlalchemy import *
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from markupsafe import escape
import requests

from app import app
from models import OckovaciMisto, VolnaMistaQuery, OckovaciKapacity

my_view = Blueprint('my_view', __name__, template_folder="templates")

@my_view.route('/')
def index():
    app.logger.info('index')
    all_data = None
    return render_template('index.html', data=all_data)

@my_view.route("/mesto/<mesto>")
def info_mesto(mesto):
    nactene_informace = app.session.query(OckovaciKapacity).from_statement(text("SELECT m.mesto, m.nazev, k.* FROM ockovaci_misto m JOIN kapacita k ON (m.misto_id=k.misto_id) where m.mesto=:mesto_param")).params(mesto_param=mesto).all()
    return render_template('mesto.html', data=nactene_informace, mesto=mesto)

@my_view.route("/misto/<misto>")
def info_misto(misto):
    nactene_informace = app.session.query(OckovaciKapacity).from_statement(text("SELECT m.mesto, m.nazev, k.* FROM ockovaci_misto m JOIN kapacita k ON (m.misto_id=k.misto_id) where m.nazev=:misto_param")).params(misto_param=misto).all()
    return render_template('misto.html', data=nactene_informace, misto=misto)

@my_view.route("/info")
def info():
    ockovani_info=app.session.query(OckovaciMisto).from_statement(text("select * from public.ockovaci_misto")).all()

    #my small test of API
    url = 'https://reservatic.com/public_services/411747/public_operations/5971/hours?date=2021-4-09'
    data = ''
    response = requests.get(url, data=data, headers={"Content-Type": "application/json"})
    #v response mam volne terminy :)
    print(response)

    #ockovani_queries = app.session.query(VolnaMistaQuery).from_statement(text("select \'https://reservatic.com/public_services/\' | | service_id | | \'/public_operations/\' | | operation_id | | \'/hours?date=\' | | d.datum from ockovaci_misto om cross join dny d")).all()
    #print(ockovani_queries)

    return render_template('ockovani_info.html', ockovaci_mista=ockovani_info, volne_terminy=response.text)
