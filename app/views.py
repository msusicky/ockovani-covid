from datetime import timedelta, date, datetime

from flask import render_template
from sqlalchemy import func, text
from werkzeug.exceptions import abort

from app import db, bp, filters, queries
from app.context import get_import_date, get_import_id, STATUS_FINISHED
from app.models import Import, Okres, Kraj, OckovaciMisto, OckovaniRegistrace, OckovaciMistoMetriky, \
    KrajMetriky, OkresMetriky


@bp.route('/')
def index():
    return render_template('index.html', last_update=_last_import_modified(), now=_now())


@bp.route("/mista")
def info_mista():
    mista = db.session.query(OckovaciMisto.id, OckovaciMisto.nazev, Okres.nazev.label("okres"),
                             Kraj.nazev.label("kraj"), OckovaciMistoMetriky.registrace_fronta,
                             OckovaciMistoMetriky.registrace_prumer_cekani, OckovaciMistoMetriky.ockovani_odhad_cekani) \
        .join(OckovaciMistoMetriky) \
        .outerjoin(Okres, (OckovaciMisto.okres_id == Okres.id)) \
        .outerjoin(Kraj, (Okres.kraj_id == Kraj.id)) \
        .filter(OckovaciMistoMetriky.datum == get_import_date()) \
        .filter(OckovaciMisto.status == True) \
        .group_by(OckovaciMisto.id, OckovaciMisto.nazev, Okres.id, Kraj.id, OckovaciMistoMetriky.registrace_fronta,
                  OckovaciMistoMetriky.registrace_prumer_cekani, OckovaciMistoMetriky.ockovani_odhad_cekani) \
        .order_by(Kraj.nazev, Okres.nazev, OckovaciMisto.nazev) \
        .all()

    return render_template('mista.html', mista=mista, last_update=_last_import_modified(), now=_now())


@bp.route("/okres/<okres_name>")
def info_okres(okres_name):
    okres = db.session.query(Okres).filter(Okres.nazev == okres_name).one_or_none()
    if okres is None:
        abort(404)

    metriky = db.session.query(OkresMetriky) \
        .filter(OkresMetriky.okres_id == okres.id, OkresMetriky.datum == get_import_date()) \
        .one_or_none()

    mista = db.session.query(OckovaciMisto.id, OckovaciMisto.nazev, Okres.nazev.label("okres"),
                             Kraj.nazev.label("kraj"), OckovaciMistoMetriky.registrace_fronta,
                             OckovaciMistoMetriky.registrace_prumer_cekani, OckovaciMistoMetriky.ockovani_odhad_cekani) \
        .join(OckovaciMistoMetriky) \
        .outerjoin(Okres, (OckovaciMisto.okres_id == Okres.id)) \
        .outerjoin(Kraj, (Okres.kraj_id == Kraj.id)) \
        .filter(Okres.nazev == okres_name) \
        .filter(OckovaciMistoMetriky.datum == get_import_date()) \
        .filter(OckovaciMisto.status == True) \
        .group_by(OckovaciMisto.id, OckovaciMisto.nazev, Okres.id, Kraj.id, OckovaciMistoMetriky.registrace_fronta,
                  OckovaciMistoMetriky.registrace_prumer_cekani, OckovaciMistoMetriky.ockovani_odhad_cekani) \
        .order_by(OckovaciMisto.nazev) \
        .all()

    registrations = queries.count_registrations('okres_id', okres.id)

    return render_template('okres.html', last_update=_last_import_modified(), now=_now(), okres=okres, metriky=metriky,
                           mista=mista, registrations=registrations)


@bp.route("/kraj/<kraj_name>")
def info_kraj(kraj_name):
    kraj = db.session.query(Kraj).filter(Kraj.nazev == kraj_name).one_or_none()
    if kraj is None:
        abort(404)

    metriky = db.session.query(KrajMetriky) \
        .filter(KrajMetriky.kraj_id == kraj.id, KrajMetriky.datum == get_import_date()) \
        .one_or_none()

    mista = db.session.query(OckovaciMisto.id, OckovaciMisto.nazev, Okres.nazev.label("okres"),
                             Kraj.nazev.label("kraj"), OckovaciMistoMetriky.registrace_fronta,
                             OckovaciMistoMetriky.registrace_prumer_cekani, OckovaciMistoMetriky.ockovani_odhad_cekani) \
        .join(OckovaciMistoMetriky) \
        .outerjoin(Okres, (OckovaciMisto.okres_id == Okres.id)) \
        .outerjoin(Kraj, (Okres.kraj_id == Kraj.id)) \
        .filter(Kraj.nazev == kraj_name) \
        .filter(OckovaciMistoMetriky.datum == get_import_date()) \
        .filter(OckovaciMisto.status == True) \
        .group_by(OckovaciMisto.id, OckovaciMisto.nazev, Okres.id, Kraj.id, OckovaciMistoMetriky.registrace_fronta,
                  OckovaciMistoMetriky.registrace_prumer_cekani, OckovaciMistoMetriky.ockovani_odhad_cekani) \
        .order_by(Okres.nazev, OckovaciMisto.nazev) \
        .all()

    vaccination_age = db.session.query("vekova_skupina", "sum_1", "sum_2", "fronta").from_statement(text(
        """
        select t1.vekova_skupina, coalesce(sum_1 - sum_2, 0) sum_1, coalesce(sum_2, 0) sum_2, coalesce(fronta, 0) fronta
        from (
            select replace(vekova_skupina, 'nezařazeno', 'neuvedeno') vekova_skupina, 
                sum(case when poradi_davky=1 then pocet else 0 end) sum_1, 
                sum(case when poradi_davky=2 then pocet else 0 end) sum_2 
            from ockovani_lide
            where kraj_nuts_kod=:kraj_kod
            group by vekova_skupina 
        ) t1
        full join (
            select vekova_skupina, sum(pocet) fronta 
            from ockovani_registrace ocr join ockovaci_mista om on (ocr.ockovaci_misto_id=om.id)
            where rezervace=False and import_id=:import_id and substr(om.okres_id, 0 ,6)=:kraj_kod
            group by vekova_skupina
        ) t2 on (t1.vekova_skupina = t2.vekova_skupina)
        order by t1.vekova_skupina
        """
    )).params(import_id=get_import_id()).params(kraj_kod=kraj.id) \
        .all()

    registrations = queries.count_registrations('kraj_id', kraj.id)

    vaccines = queries.count_vaccines_kraj(kraj.id)

    return render_template('kraj.html', last_update=_last_import_modified(), now=_now(), kraj=kraj, metriky=metriky,
                           mista=mista, vaccines=vaccines, registrations=registrations, vac_age=vaccination_age)


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

    # Compute boundary dates for rangeslider in time series chart
    dates = [i.datum for i in registrace_overview] + [j.datum_rezervace for j in registrace_overview_terminy]
    start_date = None if len(dates) == 0 else min(dates)
    end_date = None if len(dates) == 0 else max(dates)

    return render_template('misto.html', last_update=_last_import_modified(), now=_now(), misto=misto, metriky=metriky,
                           vaccines=vaccines, registrations=registrations,
                           registrace_overview=registrace_overview,
                           registrace_overview_terminy=registrace_overview_terminy,
                           start_date=start_date, end_date=end_date)


@bp.route("/mapa")
def mapa():
    mista = db.session.query(OckovaciMisto.id, OckovaciMisto.nazev, OckovaciMisto.adresa,
                             OckovaciMisto.latitude, OckovaciMisto.longitude,
                             OckovaciMisto.bezbarierovy_pristup,
                             OckovaciMistoMetriky.registrace_prumer_cekani,
                             OckovaciMistoMetriky.ockovani_odhad_cekani) \
        .join(OckovaciMistoMetriky) \
        .filter(OckovaciMisto.status == True) \
        .filter(OckovaciMistoMetriky.datum == get_import_date()) \
        .all()

    return render_template('mapa.html', last_update=_last_import_modified(), now=_now(), mista=mista)


@bp.route("/statistiky")
def statistiky():
    vaccines = queries.count_vaccines_cr()

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

    vaccination_stats = db.session.query("sum", "sum_1", "sum_2", "fronta", "termin").from_statement(text(
        """
        select sum, (sum_1 - sum_2) sum_1, sum_2, fronta, termin
        from (
            select sum(pocet) sum, 
                sum(case when poradi_davky=1 then pocet else 0 end) sum_1,
                sum(case when poradi_davky=2 then pocet else 0 end) sum_2 
            from ockovani_lide
        ) t1
        cross join (
            select sum(pocet) fronta 
            from ockovani_registrace 
            where rezervace=False and import_id=:import_id
        ) t2 
        cross join (
            select sum(maximalni_kapacita - volna_kapacita) termin 
            from ockovani_rezervace 
            where datum >= current_date and import_id=:import_id
        ) t3
        """
    )).params(import_id=get_import_id()) \
        .all()

    estimate_stats = db.session.query(
        func.sum(KrajMetriky.pocet_obyvatel_dospeli).label("pocet_obyvatel"),
        func.sum(KrajMetriky.ockovani_pocet_davek).label("ockovane_davky_celkem"),
        func.sum(KrajMetriky.ockovani_pocet_davek_zmena_tyden).label("ockovane_davky_tyden")
    ).filter(KrajMetriky.datum == get_import_date()) \
        .one_or_none()

    if estimate_stats is not None and estimate_stats.pocet_obyvatel is not None \
            and estimate_stats.ockovane_davky_celkem is not None and estimate_stats.ockovane_davky_tyden is not None:
        cr_people = estimate_stats.pocet_obyvatel
        cr_factor = 0.7
        cr_to_vacc = cr_people * cr_factor
        delka_dny = (7 * (2 * cr_to_vacc - estimate_stats.ockovane_davky_celkem)) / estimate_stats.ockovane_davky_tyden
        end_date = get_import_date() + timedelta(days=delka_dny)
    else:
        end_date = None

    vaccination_age = db.session.query("vekova_skupina", "sum_1", "sum_2", "fronta").from_statement(text(
        """
        select t1.vekova_skupina, coalesce(sum_1 - sum_2, 0) sum_1, coalesce(sum_2, 0) sum_2, coalesce(fronta, 0) fronta
        from (
            select replace(vekova_skupina, 'nezařazeno', 'neuvedeno') vekova_skupina, 
                sum(case when poradi_davky=1 then pocet else 0 end) sum_1, 
                sum(case when poradi_davky=2 then pocet else 0 end) sum_2 
            from ockovani_lide
            group by vekova_skupina 
        ) t1
        full join (
            select vekova_skupina, sum(pocet) fronta 
            from ockovani_registrace 
            where rezervace=False and import_id=:import_id
            group by vekova_skupina
        ) t2 on (t1.vekova_skupina = t2.vekova_skupina)
        order by t1.vekova_skupina
        """
    )).params(import_id=get_import_id()) \
        .all()

    return render_template('statistiky.html', last_update=_last_import_modified(), now=_now(),
                           vaccines=vaccines, end_date=end_date,
                           top5=top5_vaccination_day,
                           top5_place=top5_vaccination_place_day,
                           vac_stats=vaccination_stats, vac_age=vaccination_age)


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
