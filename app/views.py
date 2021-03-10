from datetime import timedelta, date, datetime

from flask import render_template
from sqlalchemy import func, text, case, subquery
from sqlalchemy.sql import Alias
from werkzeug.exceptions import abort

from app import db, bp, filters
from app.models import Import, Okres, Kraj, OckovaciMisto, OckovaniRegistrace, OckovaniRezervace, OckovaniLide

STATUS_FINISHED = 'FINISHED'

DAYS = 14
DAYS_MISTO = 30


@bp.route('/')
def index():
    return render_template('index.html', last_update=_last_import_modified(), now=_now())


@bp.route("/mista")
def info_mista():
    mista_rezervace_subquery = db.session.query(OckovaniRezervace.ockovaci_misto_id, func.sum(
        OckovaniRezervace.maximalni_kapacita - OckovaniRezervace.volna_kapacita).label("pocet_rezervace_f")) \
        .filter(OckovaniRezervace.import_id == _last_import_id()) \
        .filter(OckovaniRezervace.datum > datetime.today()) \
        .group_by(OckovaniRezervace.ockovaci_misto_id).subquery()

    mista_last7_subquery = db.session.query(OckovaciMisto.id.label("ockovaci_misto_id"),
                                            func.sum(OckovaniLide.pocet).label("pocet_ockovanych_tyden")) \
        .join(OckovaciMisto, (OckovaciMisto.nrpzs_kod == OckovaniLide.zarizeni_kod)) \
        .filter(OckovaniLide.datum > datetime.today() - timedelta(8)) \
        .group_by(OckovaciMisto.id).subquery()

    mista = db.session.query(OckovaciMisto.id, OckovaciMisto.nazev, Okres.nazev.label("okres"),
                             Kraj.nazev.label("kraj"),
                             func.sum(case([(OckovaniRegistrace.rezervace == False, OckovaniRegistrace.pocet), ],
                                           else_=0)).label("pocet_fronta"),
                             mista_rezervace_subquery.c.pocet_rezervace_f,
                             mista_last7_subquery.c.pocet_ockovanych_tyden) \
        .join(OckovaniRegistrace, (OckovaniRegistrace.ockovaci_misto_id == OckovaciMisto.id)) \
        .outerjoin(mista_rezervace_subquery, (OckovaciMisto.id == mista_rezervace_subquery.c.ockovaci_misto_id)) \
        .outerjoin(mista_last7_subquery, (OckovaciMisto.id == mista_last7_subquery.c.ockovaci_misto_id)) \
        .outerjoin(Okres, (OckovaciMisto.okres_id == Okres.id)) \
        .outerjoin(Kraj, (Okres.kraj_id == Kraj.id)) \
        .filter(OckovaniRegistrace.import_id == _last_import_id()) \
        .filter(OckovaciMisto.status == True) \
        .group_by(OckovaciMisto.id, OckovaciMisto.nazev, Okres.id, Kraj.id,
                  mista_rezervace_subquery.c.pocet_rezervace_f, mista_last7_subquery.c.pocet_ockovanych_tyden) \
        .order_by(Kraj.nazev, Okres.nazev, OckovaciMisto.nazev) \
        .all()

    return render_template('mista.html', mista=mista, last_update=_last_import_modified(), now=_now(), days=DAYS)


@bp.route("/okres/<okres_name>")
def info_okres(okres_name):
    okres = db.session.query(Okres).filter(Okres.nazev == okres_name).one_or_none()
    if okres is None:
        abort(404)

    mista_rezervace_subquery = db.session.query(OckovaniRezervace.ockovaci_misto_id, func.sum(
        OckovaniRezervace.maximalni_kapacita - OckovaniRezervace.volna_kapacita).label("pocet_rezervace_f")) \
        .filter(OckovaniRezervace.import_id == _last_import_id()) \
        .filter(OckovaniRezervace.datum > datetime.today()) \
        .group_by(OckovaniRezervace.ockovaci_misto_id).subquery()

    mista_last7_subquery = db.session.query(OckovaciMisto.id.label("ockovaci_misto_id"),
                                            func.sum(OckovaniLide.pocet).label("pocet_ockovanych_tyden")) \
        .join(OckovaciMisto, (OckovaciMisto.nrpzs_kod == OckovaniLide.zarizeni_kod)) \
        .filter(OckovaniLide.datum > datetime.today() - timedelta(8)) \
        .group_by(OckovaciMisto.id).subquery()

    mista = db.session.query(Okres.nazev.label("okres"), Kraj.nazev.label("kraj"), OckovaciMisto.nazev,
                             OckovaciMisto.id,
                             func.sum(case([(OckovaniRegistrace.rezervace == False, OckovaniRegistrace.pocet), ],
                                           else_=0)).label("pocet_fronta"),
                             mista_rezervace_subquery.c.pocet_rezervace_f,
                             mista_last7_subquery.c.pocet_ockovanych_tyden) \
        .join(OckovaniRegistrace, (OckovaniRegistrace.ockovaci_misto_id == OckovaciMisto.id)) \
        .outerjoin(mista_rezervace_subquery, (OckovaciMisto.id == mista_rezervace_subquery.c.ockovaci_misto_id)) \
        .outerjoin(mista_last7_subquery, (OckovaciMisto.id == mista_last7_subquery.c.ockovaci_misto_id)) \
        .outerjoin(Okres, (OckovaciMisto.okres_id == Okres.id)) \
        .outerjoin(Kraj, (Okres.kraj_id == Kraj.id)) \
        .filter(Okres.nazev == okres_name) \
        .filter(OckovaniRegistrace.import_id == _last_import_id()) \
        .filter(OckovaciMisto.status == True) \
        .group_by(Okres.id, Kraj.id, OckovaciMisto.nazev, OckovaciMisto.id,
                  mista_rezervace_subquery.c.pocet_rezervace_f, mista_last7_subquery.c.pocet_ockovanych_tyden) \
        .order_by(OckovaciMisto.nazev) \
        .all()

    return render_template('okres.html', mista=mista, okres=okres, last_update=_last_import_modified(), now=_now(),
                           days=DAYS)


@bp.route("/kraj/<kraj_name>")
def info_kraj(kraj_name):
    kraj = db.session.query(Kraj).filter(Kraj.nazev == kraj_name).one_or_none()
    if kraj is None:
        abort(404)

    mista_rezervace_subquery = db.session.query(OckovaniRezervace.ockovaci_misto_id, func.sum(
        OckovaniRezervace.maximalni_kapacita - OckovaniRezervace.volna_kapacita).label("pocet_rezervace_f")) \
        .filter(OckovaniRezervace.import_id == _last_import_id()) \
        .filter(OckovaniRezervace.datum > datetime.today()) \
        .group_by(OckovaniRezervace.ockovaci_misto_id).subquery()

    mista_last7_subquery = db.session.query(OckovaciMisto.id.label("ockovaci_misto_id"),
                                            func.sum(OckovaniLide.pocet).label("pocet_ockovanych_tyden")) \
        .join(OckovaciMisto, (OckovaciMisto.nrpzs_kod == OckovaniLide.zarizeni_kod)) \
        .filter(OckovaniLide.datum > datetime.today() - timedelta(8)) \
        .group_by(OckovaciMisto.id).subquery()

    mista = db.session.query(Okres.nazev.label("okres"), Kraj.nazev.label("kraj"), OckovaciMisto.nazev,
                             OckovaciMisto.id,
                             func.sum(case([(OckovaniRegistrace.rezervace == False, OckovaniRegistrace.pocet), ],
                                           else_=0)).label("pocet_fronta"),
                             mista_rezervace_subquery.c.pocet_rezervace_f,
                             mista_last7_subquery.c.pocet_ockovanych_tyden) \
        .join(OckovaniRegistrace, (OckovaniRegistrace.ockovaci_misto_id == OckovaciMisto.id)) \
        .outerjoin(mista_rezervace_subquery, (OckovaciMisto.id == mista_rezervace_subquery.c.ockovaci_misto_id)) \
        .outerjoin(mista_last7_subquery, (OckovaciMisto.id == mista_last7_subquery.c.ockovaci_misto_id)) \
        .outerjoin(Okres, (OckovaciMisto.okres_id == Okres.id)) \
        .outerjoin(Kraj, (Okres.kraj_id == Kraj.id)) \
        .filter(Kraj.nazev == kraj_name) \
        .filter(OckovaniRegistrace.import_id == _last_import_id()) \
        .filter(OckovaciMisto.status == True) \
        .group_by(Okres.id, Kraj.id, OckovaciMisto.nazev, OckovaciMisto.id,
                  mista_rezervace_subquery.c.pocet_rezervace_f, mista_last7_subquery.c.pocet_ockovanych_tyden) \
        .order_by(Okres.nazev, OckovaciMisto.nazev) \
        .all()

    return render_template('kraj.html', mista=mista, kraj=kraj, last_update=_last_import_modified(), now=_now(),
                           days=DAYS)


@bp.route("/misto/<misto_id>")
def info_misto(misto_id):
    misto = db.session.query(OckovaciMisto).filter(OckovaciMisto.id == misto_id).one_or_none()
    if misto is None:
        abort(404)

    registrace_info = db.session.query("vekova_skupina", "povolani", "fronta_pocet", "pomer", "rezervace_nove", "rezervace_celkem").from_statement(text(
        """
        select t1.vekova_skupina, t1.povolani, fronta_pocet, round((rezervace_nove*100.0)/rezervace_celkem) pomer, rezervace_nove, rezervace_celkem
        from (
            select vekova_skupina, povolani, sum(pocet) fronta_pocet 
            from ockovani_registrace 
            where rezervace=False and ockovaci_misto_id=:misto_id and import_id=:import_id
            group by vekova_skupina, povolani) t1
        left join (
            select vekova_skupina, povolani, sum(case when rezervace=true then pocet else 0 end) as rezervace_nove, NULLIF(sum(pocet), 0) as rezervace_celkem
            from ockovani_registrace
            where datum>now()-'7 days'::interval and ockovaci_misto_id=:misto_id and import_id=:import_id
            group by vekova_skupina, povolani
        ) t2 on (t1.vekova_skupina = t2.vekova_skupina and t1.povolani = t2.povolani) order by (t1.vekova_skupina, t1.povolani)   
        """
    )).params(misto_id=misto_id) \
        .params(import_id=_last_import_id()) \
        .all()

    ampule_info = db.session.query("vyrobce", "operace", "sum").from_statement(text(
        """
        select * from (select sum(pocet_davek ) as sum,vyrobce,\'Příjem\' as operace from ockovani_distribuce 
        where ockovaci_misto_id=:misto_id and akce=\'Příjem\' group by vyrobce union 
        (select coalesce(sum(pocet_davek ),0)as sum,vyrobce,\'Výdej\' as operace from ockovani_distribuce 
        where ockovaci_misto_id=:misto_id and akce=\'Výdej\' group by vyrobce) union 
        (select coalesce(sum(pocet_davek ),0)as sum,vyrobce,\'Příjem odjinud\' as operace from ockovani_distribuce
        where cilove_ockovaci_misto_id=:misto_id and akce=\'Výdej\' group by vyrobce)
        union ( select sum(pouzite_davky), vyrobce, \'Očkováno\' as operace
        from ockovani_spotreba where ockovaci_misto_id=:misto_id group by vyrobce)
        union (select sum(znehodnocene_davky), vyrobce, \'Zničeno\' as operace
        from ockovani_spotreba where ockovaci_misto_id=:misto_id group by vyrobce) ) as tbl
        order by vyrobce, operace
        """
    )).params(misto_id=misto_id).all()

    total = _compute_vaccination_stats(ampule_info)

    return render_template('misto.html', misto=misto, total=total, registrace_info=registrace_info,
                           last_update=_last_import_modified(), now=_now())


def _compute_vaccination_stats(ampule_info):
    # Compute  statistics
    total = {
        'Pfizer': {
            'Přijato': 0,
            'Vydáno': 0,
            'Očkováno': 0,
            'Zničeno': 0,
            'Skladem': 0,
        },
        'Moderna': {
            'Přijato': 0,
            'Vydáno': 0,
            'Očkováno': 0,
            'Zničeno': 0,
            'Skladem': 0,
        },
        'AstraZeneca': {
            'Přijato': 0,
            'Vydáno': 0,
            'Očkováno': 0,
            'Zničeno': 0,
            'Skladem': 0,
        }
    }

    for item in ampule_info:
        operation = item[1]
        if operation in ('Příjem', 'Příjem odjinud'):
            total[item[0]]['Přijato'] += item[2]
            total[item[0]]['Skladem'] += item[2]
        elif operation == 'Výdej':
            total[item[0]]['Vydáno'] += item[2]
            total[item[0]]['Skladem'] -= item[2]
        elif operation == 'Očkováno':
            total[item[0]]['Očkováno'] += item[2]
            total[item[0]]['Skladem'] -= item[2]
        elif operation == 'Zničeno':
            total[item[0]]['Zničeno'] += item[2]
            total[item[0]]['Skladem'] -= item[2]

    total = _compute_vaccination_total(total)

    return total


def _compute_vaccination_total(total):
    total_all = {
        'all': {
            'Přijato': 0,
            'Vydáno': 0,
            'Očkováno': 0,
            'Zničeno': 0,
            'Skladem': 0,
        }
    }

    for type in total.keys():
        for operation in total[type].keys():
            total_all['all'][operation] += total[type][operation]

    total.update(total_all)

    return total


@bp.route("/mapa")
def mapa():
    ockovani_info = db.session.query(OckovaciMisto.id, OckovaciMisto.nazev, OckovaciMisto.adresa,
                                     OckovaciMisto.latitude, OckovaciMisto.longitude,
                                     OckovaciMisto.bezbarierovy_pristup,
                                     Okres.nazev.label("okres"), Kraj.nazev.label("kraj"),
                                     func.sum(OckovaniRezervace.volna_kapacita).label("pocet_mist")) \
        .outerjoin(OckovaniRezervace, (OckovaniRezervace.ockovaci_misto_id == OckovaciMisto.id)) \
        .outerjoin(Okres, (OckovaciMisto.okres_id == Okres.id)) \
        .outerjoin(Kraj, (Okres.kraj_id == Kraj.id)) \
        .filter(OckovaniRezervace.datum >= date.today(),
                OckovaniRezervace.datum < date.today() + timedelta(DAYS)) \
        .filter(OckovaniRezervace.kalendar_ockovani == 'V1') \
        .filter(OckovaniRezervace.import_id == _last_import_id()) \
        .filter(OckovaciMisto.status == True) \
        .group_by(OckovaciMisto.id, OckovaciMisto.nazev, OckovaciMisto.adresa, OckovaciMisto.latitude,
                  OckovaciMisto.longitude, OckovaciMisto.bezbarierovy_pristup, Okres.id, Kraj.id) \
        .order_by(Kraj.nazev, Okres.nazev, OckovaciMisto.nazev) \
        .all()

    return render_template('mapa.html', ockovaci_mista=ockovani_info, last_update=_last_import_modified(), now=_now(),
                           days=DAYS)


@bp.route("/opendata")
def opendata():
    return render_template('opendata.html', last_update=_last_import_modified())


@bp.route("/statistiky")
def statistiky():
    # bad computation :(
    vacc_storage = db.session.query("vyrobce", "prijem", "spotreba", "rozdil").from_statement(text(
        """
        select spotrebovane.vyrobce, prijem, spotreba, prijem-spotreba as rozdil  from (
        select vyrobce, sum(pocet_davek) as prijem 
            from ockovani_distribuce where akce='Příjem' group by vyrobce) as prijate
            JOIN (        
        select case when vakcina='Comirnaty' Then 'Pfizer' when vakcina='COVID-19 Vaccine Moderna' Then 'Moderna'
	        when vakcina='COVID-19 Vaccine AstraZeneca' Then 'AstraZeneca' end as vyrobce, sum(pocet) as spotreba from ockovani_lide group by vyrobce
            ) as spotrebovane on (prijate.vyrobce=spotrebovane.vyrobce)
        """
    )).all()

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

    vaccination_stats = db.session.query("celkem", "prvni", "druha").from_statement(text(
        """
        select sum(pocet) celkem, sum(case when poradi_davky=1 then pocet else 0 end) prvni,
        sum(case when poradi_davky='2' then pocet else 0 end) druha from ockovani_lide
        """
    )).all()
    cr_people = 8670000
    cr_factor = 0.6
    cr_to_vacc = cr_people * cr_factor
    delka_dny = (cr_to_vacc - vaccination_stats[0].celkem) * 2 / top5_vaccination_day[0].sum
    end_date = date.today() + timedelta(days=delka_dny)

    vaccination_age = db.session.query("vekova_skupina", "sum_1", "sum_2").from_statement(text(
        """
        select vekova_skupina, (sum_1 - sum_2) sum_1, sum_2 
        from (
            select vekova_skupina, 
                sum(case when poradi_davky=1 then pocet else 0 end) sum_1, 
                sum(case when poradi_davky=2 then pocet else 0 end) sum_2 
            from ockovani_lide
            group by vekova_skupina order by vekova_skupina
        ) t1
        """
    )).all()

    # .params(misto_id=misto_id)

    return render_template('statistiky.html', last_update=_last_import_modified(), now=_now(),
                           vacc_storage=vacc_storage,
                           end_date=end_date,
                           top5=top5_vaccination_day,
                           top5_place=top5_vaccination_place_day,
                           vac_stats=vaccination_stats, vac_age=vaccination_age)


def _last_import_modified():
    """
    Returns last successful import.
    """
    last_modified = db.session.query(func.max(Import.last_modified)).filter(Import.status == STATUS_FINISHED).first()[0]
    if last_modified is None:
        return 'nikdy'
    else:
        return filters.format_datetime_short_wd(last_modified)


def _last_import_id():
    """
    Returns id of the last successful import.
    """
    last_id = db.session.query(func.max(Import.id)).filter(Import.status == STATUS_FINISHED).first()[0]
    if last_id is None:
        return -1
    else:
        return last_id


def _now():
    return filters.format_datetime_short_wd(datetime.now())
