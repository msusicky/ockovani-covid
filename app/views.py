from flask import render_template
from sqlalchemy import func, text
from werkzeug.exceptions import abort

from app import db, bp
from app.models import Import, Okres, Kraj, OckovaciMisto, VolnaMistaCas, VolnaMistaDen

STATUS_FINISHED = 'FINISHED'


@bp.route('/')
def index():
    return render_template('index.html', last_update=last_update())


@bp.route("/okres/<okres_nazev>")
def info_okres(okres_nazev):
    okres = db.session.query(Okres).filter(Okres.nazev == okres_nazev).one_or_none()
    if okres is None:
        abort(404)

    nactene_informace = db.session.query(Okres.nazev.label("okres"), Kraj.nazev.label("kraj"), OckovaciMisto.nazev,
                                         VolnaMistaDen.datum, VolnaMistaDen.volna_mista.label("pocet_mist"),
                                         OckovaciMisto.id) \
        .outerjoin(VolnaMistaDen, (VolnaMistaDen.misto_id == OckovaciMisto.id)) \
        .outerjoin(Okres, (OckovaciMisto.okres_id == Okres.id)) \
        .outerjoin(Kraj, (Okres.kraj_id == Kraj.id)) \
        .filter(Okres.nazev == okres_nazev) \
        .filter(
        VolnaMistaDen.import_id == last_update_import_id()).order_by(
        VolnaMistaDen.datum, OckovaciMisto.nazev).all()

    return render_template('okres.html', data=nactene_informace, okres=okres, last_update=last_update())


@bp.route("/kraj/<kraj_name>")
def info_kraj(kraj_name):
    kraj = db.session.query(Kraj).filter(Kraj.nazev == kraj_name).one_or_none()
    if kraj is None:
        abort(404)

    nactene_informace = db.session.query(Okres.nazev.label("okres"), Kraj.nazev.label("kraj"), OckovaciMisto.nazev,
                                         VolnaMistaDen.datum, VolnaMistaDen.volna_mista.label("pocet_mist"),
                                         OckovaciMisto.id) \
        .outerjoin(VolnaMistaDen, (VolnaMistaDen.misto_id == OckovaciMisto.id)) \
        .outerjoin(Okres, (OckovaciMisto.okres_id == Okres.id)) \
        .outerjoin(Kraj, (Okres.kraj_id == Kraj.id)) \
        .filter(Kraj.nazev == kraj_name) \
        .filter(
        VolnaMistaDen.import_id == last_update_import_id()).order_by(
        VolnaMistaDen.datum, OckovaciMisto.okres, OckovaciMisto.nazev).all()

    return render_template('kraj.html', data=nactene_informace, kraj=kraj, last_update=last_update())


@bp.route("/misto/<misto_id>")
def info_misto(misto_id):
    misto = db.session.query(OckovaciMisto).filter(OckovaciMisto.id == misto_id).one_or_none()
    if misto is None:
        abort(404)

    nactene_informace = db.session.query(Okres.nazev.label("okres"), Kraj.nazev.label("kraj"), OckovaciMisto.nazev,
                                         VolnaMistaDen.datum, VolnaMistaDen.volna_mista.label("pocet_mist"),
                                         OckovaciMisto.id, OckovaciMisto.adresa,
                                         OckovaciMisto.latitude, OckovaciMisto.longitude,
                                         OckovaciMisto.minimalni_kapacita,
                                         OckovaciMisto.bezbarierovy_pristup) \
        .outerjoin(VolnaMistaDen, (VolnaMistaDen.misto_id == OckovaciMisto.id)) \
        .outerjoin(Okres, (OckovaciMisto.okres_id == Okres.id)) \
        .outerjoin(Kraj, (Okres.kraj_id == Kraj.id)) \
        .filter(OckovaciMisto.id == misto.id) \
        .filter(VolnaMistaDen.import_id == last_update_import_id()).order_by(
        VolnaMistaDen.datum).all()

    ockovani_info = db.session.query(VolnaMistaDen.id, OckovaciMisto.nazev, OckovaciMisto.operation_id,
                                     Okres.nazev.label("okres"), Kraj.nazev.label("kraj"),
                                     OckovaciMisto.odkaz) \
        .outerjoin(VolnaMistaDen, (VolnaMistaDen.misto_id == OckovaciMisto.id)) \
        .outerjoin(Okres, (OckovaciMisto.okres_id == Okres.id)) \
        .outerjoin(Kraj, (Okres.kraj_id == Kraj.id)) \
        .filter(OckovaciMisto.id == misto.id) \
        .filter(VolnaMistaDen.import_id == last_update_import_id()).order_by(
        VolnaMistaDen.datum).first()

    ampule_info = db.session.query("vyrobce", "operace", "sum").from_statement(
        text("select * from (select sum(pocet_ampulek) as sum,vyrobce,\'Příjem\' as operace  from ockovani_distribuce " \
             "where ockovaci_misto_id=:misto_id and akce=\'Příjem\' group by vyrobce union " \
             "(select coalesce(sum(pocet_ampulek),0)as sum,vyrobce,\'Výdej\' as operace from ockovani_distribuce " \
             "where ockovaci_misto_id=:misto_id and akce=\'Výdej\' group by vyrobce) union " \
             "(select coalesce(sum(pocet_ampulek),0)as sum,vyrobce,\'Příjem odjinud\' as operace from ockovani_distribuce " \
             "where cilove_ockovaci_misto_id=:misto_id and akce=\'Výdej\' group by vyrobce)" \
             " union ( select sum(pouzite_ampulky), vyrobce, \'Očkováno\' as operace " \
             "from ockovani_spotreba where ockovaci_misto_id=:misto_id group by vyrobce)" \
             " union (select sum(znehodnocene_ampulky), vyrobce, \'Zničeno\' as operace" \
             " from ockovani_spotreba where ockovaci_misto_id=:misto_id group by vyrobce) ) as tbl" \
             " order by vyrobce, operace")).params(misto_id=misto_id).all()
    tot = compute_vaccination_stats(ampule_info)

    return render_template('misto.html', data=nactene_informace, misto=ockovani_info, ampule=ampule_info, total=tot,
                           last_update=last_update())


def compute_vaccination_stats(ampule_info):
    # Compute  statistics
    pf_celkem = 0;
    az_celkem = 0;
    mo_celkem = 0;
    for item in ampule_info:
        if item[0] == 'Pfizer':
            if (item[1] in ('Příjem', 'Příjem odjinud')):
                pf_celkem += item[2]
            else:
                pf_celkem -= item[2]
        if (item[0] == 'Moderna'):
            if (item[1] in ('Příjem', 'Příjem odjinud')):
                mo_celkem += item[2]
            else:
                mo_celkem -= item[2]
        if (item[0] == 'AstraZeneca'):
            if (item[1] in ('Příjem', 'Příjem odjinud')):
                az_celkem += item[2]
            else:
                az_celkem -= item[2]
    total = dict([('az', az_celkem), ('mo', mo_celkem), ('pf', pf_celkem)])
    return total


@bp.route("/mista")
def info():
    ockovani_info = db.session.query(OckovaciMisto.id, OckovaciMisto.nazev, OckovaciMisto.adresa,
                                     OckovaciMisto.latitude, OckovaciMisto.longitude,
                                     OckovaciMisto.minimalni_kapacita,
                                     OckovaciMisto.bezbarierovy_pristup,
                                     OckovaciMisto.service_id,
                                     OckovaciMisto.operation_id, OckovaciMisto.odkaz,
                                     Okres.nazev.label("okres"), Kraj.nazev.label("kraj"),
                                     func.sum(VolnaMistaDen.volna_mista).label("pocet_mist")) \
        .outerjoin(VolnaMistaDen, (VolnaMistaDen.misto_id == OckovaciMisto.id)) \
        .outerjoin(Okres, (OckovaciMisto.okres_id == Okres.id)) \
        .outerjoin(Kraj, (Okres.kraj_id == Kraj.id)) \
        .filter(VolnaMistaDen.import_id == last_update_import_id() and (
            OckovaciMisto.status is True or OckovaciMisto.status is None)) \
        .group_by(OckovaciMisto.id, OckovaciMisto.nazev, OckovaciMisto.adresa, OckovaciMisto.latitude,
                  OckovaciMisto.longitude, OckovaciMisto.minimalni_kapacita, OckovaciMisto.bezbarierovy_pristup,
                  OckovaciMisto.service_id, OckovaciMisto.operation_id, OckovaciMisto.odkaz,
                  Okres.nazev, Kraj.nazev) \
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
