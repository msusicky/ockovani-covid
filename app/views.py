from datetime import timedelta, datetime

from flask import render_template
from sqlalchemy import func, text
from werkzeug.exceptions import abort

from app import db, bp, filters, queries
from app.context import get_import_date, STATUS_FINISHED
from app.models import Import, Okres, Kraj, OckovaciMisto, OckovaciMistoMetriky, KrajMetriky, OkresMetriky, CrMetriky


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

    vaccination_doctors = queries.count_vaccinated_doctors(kraj.id)

    queue_graph_data = queries.get_queue_graph_data(kraj_id=kraj.id)

    return render_template('kraj.html', last_update=_last_import_modified(), now=_now(), kraj=kraj, metriky=metriky,
                           mista=mista, vaccines=vaccines, registrations=registrations, vaccinated=vaccinated,
                           vaccination_doctors=vaccination_doctors,
                           queue_graph_data=queue_graph_data)


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

    queue_graph_data = queries.get_queue_graph_data(center_id=misto_id)

    registrations_graph_data = queries.get_registrations_graph_data(misto_id)

    vaccination_graph_data = queries.get_vaccination_graph_data(misto_id)

    return render_template('misto.html', last_update=_last_import_modified(), now=_now(), misto=misto, metriky=metriky,
                           vaccines=vaccines, registrations=registrations, queue_graph_data=queue_graph_data,
                           registrations_graph_data=registrations_graph_data,
                           vaccination_graph_data=vaccination_graph_data)


@bp.route("/mapa")
def mapa():
    mista = queries.find_centers(OckovaciMisto.status, True)

    return render_template('mapa.html', last_update=_last_import_modified(), now=_now(), mista=mista)


@bp.route("/statistiky")
def statistiky():
    metriky = db.session.query(CrMetriky) \
        .filter(CrMetriky.datum == get_import_date()) \
        .one_or_none()

    end_date = queries.count_end_date_vaccinated()

    end_date_supplies = queries.count_end_date_supplies()

    vaccines = queries.count_vaccines_cr()

    vaccinated = queries.count_vaccinated()

    supplies = queries.count_supplies()

    vaccinated_category = queries.count_vaccinated_category()

    reservations_category = queries.count_reservations_category()

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

    # Source data for graph of received vaccines of the manufacturers
    received_vaccine_graph_data = queries.get_received_vaccine_graph_data()

    # Source data for graph of used vaccines based on the manufacturers
    used_vaccine_graph_data = queries.get_used_vaccine_graph_data()

    # Source data for graph of people in queue for the whole republic
    queue_graph_data = queries.get_queue_graph_data()

    infected_graph_data = queries.get_infected_graph_data()

    deaths_graph_data = queries.get_deaths_graph_data()

    if metriky is not None and metriky.ockovani_pocet_davek_zmena_tyden is not None:
        cr_people = metriky.pocet_obyvatel_dospeli
        cr_factor = 0.7
        cr_to_vacc = cr_people * cr_factor
        delka_dny = (7 * (2 * cr_to_vacc - metriky.ockovani_pocet_davek)) / metriky.ockovani_pocet_davek_zmena_tyden
        end_date = get_import_date() + timedelta(days=delka_dny)
    else:
        end_date = None

    return render_template('statistiky.html', last_update=_last_import_modified(), now=_now(), metriky=metriky,
                           vaccines=vaccines, vaccinated=vaccinated, supplies=supplies, end_date=end_date,
                           vaccinated_category=vaccinated_category, reservations_category=reservations_category,
                           end_date_supplies=end_date_supplies, top5=top5_vaccination_day,
                           top5_place=top5_vaccination_place_day,
                           received_vaccine_graph_data=received_vaccine_graph_data,
                           used_vaccine_graph_data=used_vaccine_graph_data,
                           queue_graph_data=queue_graph_data, infected_graph_data=infected_graph_data,
                           deaths_graph_data=deaths_graph_data)


@bp.route("/napoveda")
def napoveda():
    return render_template('napoveda.html', last_update=_last_import_modified(), now=_now())


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
