from flask import Blueprint, render_template
from sqlalchemy import *
from sqlalchemy import text

from app import app
from models import OckovaciMisto, OckovaciKapacity, ImportLog, Kapacita

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
            "WHERE m.misto_id=:misto_param "
            "ORDER BY k.datum"
        )
    ).params(misto_param=misto).all()

    ockovani_info = app.session.query(OckovaciMisto).from_statement(text(
        "SELECT m.misto_id, m.nazev, m.service_id, m.operation_id, m.place_id, m.mesto "
        "FROM public.ockovaci_misto m "
        "WHERE m.misto_id=:misto_param"
    )).params(misto_param=misto).first()

    return render_template('misto.html', data=nactene_informace, misto=ockovani_info, last_update=last_update())


@my_view.route("/info")
def info():
    ockovani_info = app.session.query(OckovaciMisto.misto_id, OckovaciMisto.nazev, OckovaciMisto.service_id,
                                      OckovaciMisto.operation_id,
                                      OckovaciMisto.place_id, OckovaciMisto.mesto,
                                      func.max(Kapacita.pocet_mist).label("pocet_mist")).outerjoin(Kapacita, Kapacita.misto_id == OckovaciMisto.misto_id).group_by(
        OckovaciMisto.misto_id, OckovaciMisto.nazev, OckovaciMisto.service_id, OckovaciMisto.operation_id,
        OckovaciMisto.place_id, OckovaciMisto.mesto).all()
    return render_template('ockovani_info.html', ockovaci_mista=ockovani_info, last_update=last_update())


def last_update():
    last_run = app.session.query(func.max(ImportLog.spusteni)).first()[0]
    if last_run is None:
        last_run_formatted = 'nikdy'
    else:
        last_run_formatted = last_run.strftime('%d. %m. %Y %H:%M')

    return last_run_formatted
