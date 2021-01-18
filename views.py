from flask import Blueprint, render_template, g, session, redirect, url_for, request
from sqlalchemy import *
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from markupsafe import escape
import requests

from app import app
from models import OckovaciMisto, VolnaMistaQuery, OckovaciKapacity, ImportLog

my_view = Blueprint('my_view', __name__, template_folder="templates")


@my_view.route('/')
def index():
    app.logger.info('index')
    all_data = None
    return render_template('index.html', data=all_data, last_update=last_update())


@my_view.route("/mesto/<mesto>")
def info_mesto(mesto):
    nactene_informace = app.session.query(OckovaciKapacity).from_statement(
        text(
            "SELECT m.mesto, m.nazev, k.datum, k.pocet_mist, k.misto_id FROM ockovaci_misto m "
            "JOIN kapacita k ON (m.misto_id=k.misto_id) "
            "WHERE m.mesto=:mesto_param "
            "ORDER BY k.datum, m.nazev"
        )
    ).params(mesto_param=mesto).all()
    return render_template('mesto.html', data=nactene_informace, mesto=mesto, last_update=last_update())


@my_view.route("/misto/<misto>")
def info_misto(misto):
    nactene_informace = app.session.query(OckovaciKapacity).from_statement(
        text(
            "SELECT m.mesto, m.nazev, k.datum, k.pocet_mist, k.misto_id FROM ockovaci_misto m "
            "JOIN kapacita k ON (m.misto_id=k.misto_id) "
            "WHERE m.nazev=:misto_param "
            "ORDER BY k.datum"
        )
    ).params(misto_param=misto).all()
    return render_template('misto.html', data=nactene_informace, misto=misto, last_update=last_update())


@my_view.route("/info")
def info():
    ockovani_info = app.session.query(OckovaciMisto).from_statement(text(
        "SELECT om.misto_id, om.nazev, om.service_id, om.operation_id, om.place_id, om.mesto, sum(pocet_mist) pocet_mist "
        "FROM public.ockovaci_misto om left join kapacita k on (om.misto_id=k.misto_id) "
        "GROUP BY om.misto_id, om.nazev, om.service_id, om.operation_id, om.place_id, om.mesto "
        "ORDER BY mesto, nazev")).all()

    return render_template('ockovani_info.html', ockovaci_mista=ockovani_info, last_update=last_update())


def last_update():
    try:
        last_run = app.session.query(ImportLog).from_statement(text(
            "SELECT max(spusteni) FROM import_log")).first()
    except:
        last_run = 'nikdy'
    return last_run
