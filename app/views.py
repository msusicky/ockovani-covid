from flask import render_template, Blueprint
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.exceptions import abort

from app import app, db, bp
from app.models import Import, Okres, Kraj, OckovaciMisto, VolnaMista

STATUS_FINISHED = 'FINISHED'


@bp.route('/')
def index():
    return render_template('index.html', last_update=last_update())


@bp.route("/okres/<okres_id>")
def info_okres(okres_id):
    okres = db.session.query(Okres).filter(Okres.id == okres_id).one_or_none()
    if okres is None:
        abort(404)

    # nactene_informace = app.session.query(OckovaciKapacity).from_statement(
    #     text(
    #         "SELECT m.mesto, m.kraj, m.nazev, k.datum, k.pocet_mist, m.misto_id, k.kapacita_id FROM ockovaci_misto m "
    #         "JOIN kapacita k ON (m.misto_id=k.misto_id OR (m.covtest_id = k.covtest_id)) "
    #         "WHERE m.mesto=:mesto_param and k.import_id=(SELECT max(import_id) FROM import_log WHERE status=:status_param)"
    #         "ORDER BY k.datum, m.nazev"
    #     )
    # ).params(mesto_param=mesto, status_param=STATUS_FINISHED).all()
    # # TODO casem zmenit to max_import_id

    nactene_informace = []

    return render_template('okres.html', data=nactene_informace, okres=okres, last_update=last_update())


@bp.route("/kraj/<kraj_id>")
def info_kraj(kraj_id):
    kraj = db.session.query(Kraj).filter(Kraj.id == kraj_id).one_or_none()
    if kraj is None:
        abort(404)

    # nactene_informace = app.session.query(OckovaciKapacity).from_statement(
    #     text(
    #         "SELECT m.mesto, m.kraj, m.nazev, k.datum, k.pocet_mist, m.misto_id, k.kapacita_id FROM ockovaci_misto m "
    #         "JOIN kapacita k ON (m.misto_id=k.misto_id OR (m.covtest_id = k.covtest_id)) "
    #         "WHERE m.kraj=:kraj_param and k.import_id=(SELECT max(import_id) FROM import_log WHERE status=:status_param)"
    #         "ORDER BY k.datum, m.mesto, m.nazev"
    #     )
    # ).params(kraj_param=kraj, status_param=STATUS_FINISHED).all()

    nactene_informace = []

    print(kraj)

    return render_template('kraj.html', data=nactene_informace, kraj=kraj, last_update=last_update())


@bp.route("/misto/<misto>")
def info_misto(misto):
    # nactene_informace = app.session.query(OckovaciKapacity).from_statement(
    #     text(
    #         "SELECT m.mesto, m.kraj, m.nazev, k.datum, k.pocet_mist, m.misto_id, k.kapacita_id FROM ockovaci_misto m "
    #         "JOIN kapacita k ON (m.misto_id=k.misto_id OR (m.covtest_id = k.covtest_id)) "
    #         "WHERE m.misto_id=:misto_param and k.import_id=(SELECT max(import_id) FROM import_log WHERE status=:status_param)"
    #         "ORDER BY k.datum"
    #     )
    # ).params(misto_param=misto, status_param=STATUS_FINISHED).all()
    #
    # ockovani_info = app.session.query(OckovaciMisto).from_statement(text(
    #     "SELECT m.misto_id, m.nazev, m.service_id, m.operation_id, m.place_id, m.mesto, m.kraj, m.nazev_odkaz "
    #     "FROM public.ockovaci_misto m "
    #     "WHERE m.misto_id=:misto_param"
    # )).params(misto_param=misto).first()

    nactene_informace = []
    ockovani_info = []

    return render_template('misto.html', data=nactene_informace, misto=ockovani_info, last_update=last_update())


@bp.route("/mista")
def info():
    ockovani_info = db.session.query(OckovaciMisto.id, OckovaciMisto.nazev, OckovaciMisto.adresa,
                                     OckovaciMisto.latitude, OckovaciMisto.longitude, OckovaciMisto.minimalni_kapacita,
                                     OckovaciMisto.bezbarierovy_pristup,
                                     OckovaciMisto.service_id,
                                     OckovaciMisto.operation_id, OckovaciMisto.odkaz,
                                     Okres.nazev.label("okres"), Kraj.nazev.label("kraj"),
                                     func.sum(VolnaMista.volna_mista).label("pocet_mist")) \
        .outerjoin(VolnaMista, (VolnaMista.misto_id == OckovaciMisto.id)) \
        .outerjoin(Okres, (OckovaciMisto.okres_id == Okres.id)) \
        .outerjoin(Kraj, (Okres.kraj_id == Kraj.id)) \
        .filter(VolnaMista.import_id == last_update_import_id() and (
                OckovaciMisto.status != True or OckovaciMisto.status is None)) \
        .group_by(OckovaciMisto.id, OckovaciMisto.nazev, OckovaciMisto.adresa, OckovaciMisto.latitude,
                  OckovaciMisto.longitude, OckovaciMisto.minimalni_kapacita, OckovaciMisto.bezbarierovy_pristup,
                  OckovaciMisto.service_id, OckovaciMisto.operation_id, OckovaciMisto.odkaz, Kraj.nazev, Okres.nazev) \
        .order_by(Kraj.nazev, Okres.nazev, OckovaciMisto.nazev).all()

    return render_template('mista.html', ockovaci_mista=ockovani_info, last_update=last_update())


def last_update():
    last_import = db.session.query(func.max(Import.start)).filter(Import.status == STATUS_FINISHED).first()[0]
    if last_import is None:
        last_import_datetime = 'nikdy'
    else:
        last_import_datetime = last_import.strftime('%d. %m. %Y %H:%M')

    return last_import_datetime


def last_update_import_id():
    """
    For better filtering.
    @return:
    """
    last_run = db.session.query(func.max(Import.id)).filter(Import.status == STATUS_FINISHED).first()[0]
    if last_run is None:
        max_import_id = -1
    else:
        max_import_id = last_run

    return max_import_id
