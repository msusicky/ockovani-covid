from flask import render_template
from sqlalchemy import func

from app import app, db
from app.models import Import

STATUS_FINISHED = 'FINISHED'


@app.route('/')
def index():
    app.logger.info('index')
    return render_template('index.html', last_update=last_update())


@app.route("/mesto/<okres>")
def info_okres(mesto):
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

    return render_template('okres.html', data=nactene_informace, mesto=mesto, last_update=last_update())


@app.route("/kraj/<kraj>")
def info_kraj(kraj):
    # nactene_informace = app.session.query(OckovaciKapacity).from_statement(
    #     text(
    #         "SELECT m.mesto, m.kraj, m.nazev, k.datum, k.pocet_mist, m.misto_id, k.kapacita_id FROM ockovaci_misto m "
    #         "JOIN kapacita k ON (m.misto_id=k.misto_id OR (m.covtest_id = k.covtest_id)) "
    #         "WHERE m.kraj=:kraj_param and k.import_id=(SELECT max(import_id) FROM import_log WHERE status=:status_param)"
    #         "ORDER BY k.datum, m.mesto, m.nazev"
    #     )
    # ).params(kraj_param=kraj, status_param=STATUS_FINISHED).all()

    nactene_informace = []

    return render_template('kraj.html', data=nactene_informace, kraj=kraj, last_update=last_update())


@app.route("/misto/<misto>")
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


@app.route("/info")
def info():
    # ockovani_info = app.session.query(OckovaciMisto.misto_id, OckovaciMisto.nazev, OckovaciMisto.service_id,
    #                                   OckovaciMisto.operation_id, OckovaciMisto.place_id, OckovaciMisto.mesto,
    #                                   OckovaciMisto.kraj, func.sum(Kapacita.pocet_mist).label("pocet_mist")) \
    #     .outerjoin(Kapacita, (Kapacita.misto_id == OckovaciMisto.misto_id) | (Kapacita.covtest_id == OckovaciMisto.covtest_id)) \
    #     .filter(Kapacita.import_id == last_update_import_id()) \
    #     .group_by(OckovaciMisto.misto_id, OckovaciMisto.nazev, OckovaciMisto.service_id, OckovaciMisto.operation_id,
    #               OckovaciMisto.place_id, OckovaciMisto.mesto, OckovaciMisto.kraj) \
    #     .order_by(OckovaciMisto.kraj, OckovaciMisto.mesto, OckovaciMisto.nazev) \
    #     .all()
    ockovani_info = []

    return render_template('mista.html', ockovaci_mista=ockovani_info, last_update=last_update())


def last_update():
    last_import = db.session.query(func.max(Import.start)).filter(Import.status == STATUS_FINISHED).first()[0]
    if last_import is None:
        last_import_datetime = 'nikdy'
    else:
        last_import_datetime = last_import.strftime('%d. %m. %Y %H:%M')

    return last_import_datetime
#
#
# def last_update_import_id():
#     """
#     For better filtering.
#     @return:
#     """
#     last_run = app.session.query(func.max(ImportLog.import_id)).filter(ImportLog.status == STATUS_FINISHED).first()[0]
#     if last_run is None:
#         max_import_id = -1
#     else:
#         max_import_id = last_run
#
#     return max_import_id
