from datetime import timedelta, date, datetime

from flask import render_template
from sqlalchemy import func, text, or_
from werkzeug.exceptions import abort

from app import db, bp, filters, queries
from app.context import get_import_date, get_import_id, STATUS_FINISHED
from app.models import Import, Okres, Kraj, OckovaciMisto, OckovaniRegistrace, OckovaciMistoMetriky, \
    KrajMetriky, OkresMetriky, CrMetriky


@bp.route('/')
def index():
    return render_template('index.html', last_update=_last_import_modified(), now=_now())


@bp.route("/mista")
def info_mista():
    mista = queries.find_centers(True, True)

    return render_template('mista.html', mista=mista, last_update=_last_import_modified(), now=_now())


@bp.route("/okres/<okres_name>")
def info_okres(okres_name):
    okres = db.session.query(Okres).filter(Okres.nazev == okres_name).one_or_none()
    if okres is None:
        abort(404)

    mista = queries.find_centers(Okres.id, okres.id)

    metriky = db.session.query(OkresMetriky) \
        .filter(OkresMetriky.okres_id == okres.id, OkresMetriky.datum == get_import_date()) \
        .one_or_none()

    registrations = queries.count_registrations('okres_id', okres.id)

    return render_template('okres.html', last_update=_last_import_modified(), now=_now(), okres=okres, metriky=metriky,
                           mista=mista, registrations=registrations)


@bp.route("/kraj/<kraj_name>")
def info_kraj(kraj_name):
    kraj = db.session.query(Kraj).filter(Kraj.nazev == kraj_name).one_or_none()
    if kraj is None:
        abort(404)

    mista = queries.find_centers(Kraj.id, kraj.id)

    metriky = db.session.query(KrajMetriky) \
        .filter(KrajMetriky.kraj_id == kraj.id, KrajMetriky.datum == get_import_date()) \
        .one_or_none()

    registrations = queries.count_registrations('kraj_id', kraj.id)

    vaccines = queries.count_vaccines_kraj(kraj.id)

    vaccinated = queries.count_vaccinated(kraj.id)

    return render_template('kraj.html', last_update=_last_import_modified(), now=_now(), kraj=kraj, metriky=metriky,
                           mista=mista, vaccines=vaccines, registrations=registrations, vaccinated=vaccinated)


@bp.route("/misto/<misto_id>")
def info_misto(misto_id):
    misto = db.session.query(OckovaciMisto).filter(OckovaciMisto.id == misto_id).one_or_none()
    if misto is None:
        abort(404)

    metriky = db.session.query(OckovaciMistoMetriky) \
        .filter(OckovaciMistoMetriky.misto_id == misto_id, OckovaciMistoMetriky.datum == get_import_date()) \
        .one_or_none()

    registrations = queries.count_registrations('ockovaci_mista.id', misto_id)

    vaccines = queries.count_vaccines_center(misto_id)

    # Source data for plotly graph
    registrace_overview = db.session.query(
        OckovaniRegistrace.datum,
        func.sum(OckovaniRegistrace.pocet).label("pocet_registrovanych")) \
        .filter(OckovaniRegistrace.import_id == get_import_id()) \
        .filter(OckovaniRegistrace.ockovaci_misto_id == misto.id) \
        .filter(OckovaniRegistrace.datum.between(date.today() - timedelta(days=365), date.today())) \
        .group_by(OckovaniRegistrace.datum) \
        .order_by(OckovaniRegistrace.datum).all()

    registrace_overview_terminy = db.session.query(
        OckovaniRegistrace.datum_rezervace,
        func.sum(OckovaniRegistrace.pocet).label("pocet_terminu")) \
        .filter(OckovaniRegistrace.import_id == get_import_id()) \
        .filter(OckovaniRegistrace.ockovaci_misto_id == misto.id) \
        .filter(OckovaniRegistrace.datum_rezervace > date.today() - timedelta(days=365)) \
        .group_by(OckovaniRegistrace.datum_rezervace) \
        .order_by(OckovaniRegistrace.datum_rezervace).all()

    queue_graph_data = db.session.query(OckovaciMistoMetriky.datum, OckovaciMistoMetriky.registrace_fronta,
                             OckovaciMistoMetriky.rezervace_cekajici_1, OckovaciMistoMetriky.rezervace_cekajici_2) \
        .filter(OckovaciMistoMetriky.misto_id == misto.id) \
        .filter(or_(OckovaciMistoMetriky.registrace_fronta > 0, OckovaciMistoMetriky.rezervace_cekajici_1 > 0,
                    OckovaciMistoMetriky.rezervace_cekajici_2 > 0)) \
        .order_by(OckovaciMistoMetriky.datum) \
        .all()

    return render_template('misto.html', last_update=_last_import_modified(), now=_now(), misto=misto, metriky=metriky,
                           vaccines=vaccines, registrations=registrations, queue_graph_data=queue_graph_data,
                           registrace_overview=registrace_overview,
                           registrace_overview_terminy=registrace_overview_terminy)


@bp.route("/mapa")
def mapa():
    mista = queries.find_centers(OckovaciMisto.status, True)

    return render_template('mapa.html', last_update=_last_import_modified(), now=_now(), mista=mista)


@bp.route("/statistiky")
def statistiky():
    metriky = db.session.query(CrMetriky) \
        .filter(CrMetriky.datum == get_import_date()) \
        .one_or_none()

    vaccines = queries.count_vaccines_cr()

    vaccinated = queries.count_vaccinated()

    top5_vaccination_day = db.session.query("datum", "sum").from_statement(text(
        """
        select datum, sum(pocet) from ockovani_lide 
        group by datum order by sum(pocet) desc limit 5
        """
    )).all()

    top5_vaccination_place_day = db.session.query("datum", "zarizeni_nazev", "sum").from_statement(text(
        """
        select datum, zarizeni_nazev, sum(pocet) from ockovani_lide 
        group by datum, zarizeni_nazev order by sum(pocet) desc limit 5;
        """
    )).all()

    if metriky is not None and metriky.ockovani_pocet_davek_zmena_tyden is not None:
        cr_people = metriky.pocet_obyvatel_dospeli
        cr_factor = 0.7
        cr_to_vacc = cr_people * cr_factor
        delka_dny = (7 * (2 * cr_to_vacc - metriky.ockovani_pocet_davek)) / metriky.ockovani_pocet_davek_zmena_tyden
        end_date = get_import_date() + timedelta(days=delka_dny)
    else:
        end_date = None

    return render_template('statistiky.html', last_update=_last_import_modified(), now=_now(), metriky=metriky,
                           vaccines=vaccines, vaccinated=vaccinated, end_date=end_date,
                           top5=top5_vaccination_day, top5_place=top5_vaccination_place_day)


@bp.route("/codelat")
def codelat():
    return render_template('codelat.html', last_update=_last_import_modified(), now=_now())


@bp.route("/odkazy")
def odkazy():
    return render_template('odkazy.html', last_update=_last_import_modified(), now=_now())


def _last_import_modified():
    """
    Returns last successful import.
    """
    last_modified = db.session.query(func.max(Import.last_modified)) \
        .filter(Import.status == STATUS_FINISHED) \
        .first()[0]
    return 'nikdy' if last_modified is None else filters.format_datetime_short_wd(last_modified)


def _now():
    return filters.format_datetime_short_wd(datetime.now())
