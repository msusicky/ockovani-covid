from datetime import datetime

from flask import render_template, session
from sqlalchemy import func, text
from werkzeug.exceptions import abort

from app import db, bp, filters, queries
from app.context import get_import_date, get_import_id, STATUS_FINISHED
from app.models import Import, Okres, Kraj, OckovaciMisto, OckovaciMistoMetriky, KrajMetriky, OkresMetriky, CrMetriky, \
    PrakticiLogin, PrakticiKapacity, ZdravotnickeStredisko, OckovaciMistoBezRegistrace


@bp.route('/')
def index():
    return render_template('index.html', last_update=_last_import_modified(), now=_now())


@bp.route("/mista")
def info_mista():
    mista = queries.find_centers(True, True)

    third_doses_centers = queries.find_third_doses_centers()

    return render_template('mista.html', mista=mista, last_update=_last_import_modified(), now=_now(),
                           third_doses_centers=third_doses_centers)


@bp.route("/okres/<okres_name>")
def info_okres(okres_name):
    okres = db.session.query(Okres).filter(Okres.nazev == okres_name).one_or_none()
    if okres is None:
        abort(404)

    mista = queries.find_centers(Okres.id, okres.id)

    third_doses_centers = queries.find_third_doses_centers()

    metriky = db.session.query(OkresMetriky) \
        .filter(OkresMetriky.okres_id == okres.id, OkresMetriky.datum == get_import_date()) \
        .one_or_none()

    registrations = queries.count_registrations('okres_id', okres.id)

    return render_template('okres.html', last_update=_last_import_modified(), now=_now(), okres=okres, metriky=metriky,
                           mista=mista, third_doses_centers=third_doses_centers, registrations=registrations)


@bp.route("/kraj/<kraj_name>")
def info_kraj(kraj_name):
    kraj = db.session.query(Kraj).filter(Kraj.nazev == kraj_name).one_or_none()
    if kraj is None:
        abort(404)

    mista = queries.find_centers(Kraj.id, kraj.id)

    third_doses_centers = queries.find_third_doses_centers()

    metriky = db.session.query(KrajMetriky) \
        .filter(KrajMetriky.kraj_id == kraj.id, KrajMetriky.datum == get_import_date()) \
        .one_or_none()

    registrations = queries.count_registrations('kraj_id', kraj.id)

    vaccines = queries.count_vaccines_kraj(kraj.id)

    vaccinated = queries.count_vaccinated(kraj.id)

    vaccination_doctors = queries.count_vaccinated_doctors(kraj.id)

    queue_graph_data = queries.get_queue_graph_data(kraj_id=kraj.id)

    return render_template('kraj.html', last_update=_last_import_modified(), now=_now(), kraj=kraj, metriky=metriky,
                           mista=mista, third_doses_centers=third_doses_centers, vaccines=vaccines,
                           registrations=registrations, vaccinated=vaccinated, vaccination_doctors=vaccination_doctors,
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

    free_slots = queries.count_free_slots(misto_id)

    vaccines = queries.count_vaccines_center(misto_id)

    queue_graph_data = queries.get_queue_graph_data(center_id=misto_id)

    registrations_graph_data = queries.get_registrations_graph_data(misto_id)

    vaccination_graph_data = queries.get_vaccination_graph_data(misto_id)

    opening_hours = {}
    for oh in misto.provozni_doba:
        if oh.den not in opening_hours:
            opening_hours[oh.den] = []
        opening_hours[oh.den].append((oh.od, oh.do))

    return render_template('misto.html', last_update=_last_import_modified(), now=_now(), misto=misto, metriky=metriky,
                           vaccines=vaccines, registrations=registrations, free_slots=free_slots,
                           queue_graph_data=queue_graph_data, registrations_graph_data=registrations_graph_data,
                           vaccination_graph_data=vaccination_graph_data, opening_hours=opening_hours)


@bp.route("/mapa")
def mapa():
    mista = queries.find_centers(True, True)

    third_doses_centers = queries.find_third_doses_centers()

    return render_template('mapa.html', last_update=_last_import_modified(), now=_now(), mista=mista,
                           third_doses_centers=third_doses_centers)


@bp.route("/praktici")
def praktici():
    vaccination_doctors = queries.count_vaccinated_doctors()

    free_vaccines = queries.find_free_vaccines_available()

    vaccines_options = queries.find_free_vaccines_vaccine_options()

    kraj_options = queries.find_free_vaccines_kraj_options()

    return render_template('praktici.html', last_update=_last_import_modified(), now=_now(),
                           vaccination_doctors=vaccination_doctors, free_vaccines=free_vaccines,
                           vaccines_options=vaccines_options, kraj_options=kraj_options)


@bp.route("/statistiky")
def statistiky():
    metriky = db.session.query(CrMetriky) \
        .filter(CrMetriky.datum == get_import_date()) \
        .one_or_none()

    end_date = queries.count_end_date_vaccinated()

    end_date_supplies = queries.count_end_date_supplies()

    end_date_interested = queries.count_end_date_interested()

    interest = queries.count_interest()

    vaccines = queries.count_vaccines_cr()

    vaccinated = queries.count_vaccinated()

    supplies = queries.count_supplies()

    end_date_category = queries.count_end_date_category()

    vaccinated_category = queries.count_vaccinated_category()

    reservations_category = queries.count_reservations_category()

    vaccinated_week = queries.count_vaccinated_week()

    top_centers = queries.count_top_centers()

    vaccinated_unvaccinated_comparison_age = queries.count_vaccinated_unvaccinated_comparison_age()

    # Source data for graph of received vaccines of the manufacturers
    received_vaccine_graph_data = queries.get_received_vaccine_graph_data()

    # Source data for graph of used vaccines based on the manufacturers
    used_vaccine_graph_data = queries.get_used_vaccine_graph_data()

    # Source data for graph of people in queue for the whole republic
    queue_graph_data = queries.get_queue_graph_data()

    vaccination_total_graph_data = queries.get_vaccination_total_graph_data()

    registrations_graph_data = queries.get_registrations_graph_data()

    infected_graph_data = queries.get_infected_graph_data()

    deaths_graph_data = queries.get_deaths_graph_data()

    pocet_opravneni = queries.count_eligible()

    infected_orp_graph_data = queries.get_infected_orp_graph_data()

    vaccinated_orp_graph_data = queries.get_vaccinated_orp_graph_data()

    hospitalized_orp_graph_data = queries.get_hospitalized_orp_graph_data()

    tests_orp_graph_data = queries.get_tests_orp_graph_data()

    return render_template('statistiky.html', last_update=_last_import_modified(), now=_now(), metriky=metriky,
                           end_date=end_date, end_date_supplies=end_date_supplies,
                           end_date_interested=end_date_interested, interest=interest, vaccines=vaccines,
                           vaccinated=vaccinated, vaccinated_category=vaccinated_category,
                           reservations_category=reservations_category, supplies=supplies,
                           end_date_category=end_date_category, vaccinated_week=vaccinated_week,
                           top_centers=top_centers,
                           vaccinated_unvaccinated_comparison_age=vaccinated_unvaccinated_comparison_age,
                           received_vaccine_graph_data=received_vaccine_graph_data,
                           used_vaccine_graph_data=used_vaccine_graph_data, queue_graph_data=queue_graph_data,
                           vaccination_total_graph_data=vaccination_total_graph_data,
                           registrations_graph_data=registrations_graph_data,
                           infected_graph_data=infected_graph_data, deaths_graph_data=deaths_graph_data,
                           pocet_opravneni=pocet_opravneni, infected_orp_graph_data=infected_orp_graph_data,
                           vaccinated_orp_graph_data=vaccinated_orp_graph_data,
                           hospitalized_orp_graph_data=hospitalized_orp_graph_data,
                           tests_orp_graph_data=tests_orp_graph_data)


@bp.route("/napoveda")
def napoveda():
    return render_template('napoveda.html', last_update=_last_import_modified(), now=_now())


@bp.route("/odkazy")
def odkazy():
    return render_template('odkazy.html', last_update=_last_import_modified(), now=_now())


@bp.route("/dataquality")
def dataquality():
    susp_vaccination_type = db.session.query("datum", "vakcina", "zarizeni_kod", "zarizeni_nazev", "vekova_skupina",
                                             "pocet").from_statement(text(
        """
        select datum, vakcina, zarizeni_kod, zarizeni_nazev, vekova_skupina, pocet 
        from ockovani_lide where vakcina not in ('Comirnaty','VAXZEVRIA','Spikevax', 'COVID-19 Vaccine Janssen')
        """
    )).all()

    susp_vaccination_age = db.session.query("datum", "vakcina", "zarizeni_kod", "zarizeni_nazev", "vekova_skupina",
                                            "pocet").from_statement(text(
        """
        select datum, vakcina, zarizeni_kod, zarizeni_nazev, vekova_skupina, pocet 
        from ockovani_lide where vakcina !='Comirnaty' and vekova_skupina='0-17'
        """
    )).all()

    susp_storage_vacc = db.session.query("pomer", "vakciny_skladem_pocet", "ockovani_pocet_davek",
                                         "nazev").from_statement(text(
        """
        select ockovani_pocet_davek/vakciny_skladem_pocet pomer,vakciny_skladem_pocet, ockovani_pocet_davek, om.nazev from ockovaci_mista_metriky omm
            join ockovaci_mista om on (omm.misto_id=om.id)
            where vakciny_skladem_pocet>200 and (ockovani_pocet_davek*1.0/vakciny_skladem_pocet<0.15)
            and omm.datum+'2 day'::interval>'{}'
        """.format(get_import_date())
    )).all()

    susp_vaccination = db.session.query("vakciny_prijate_pocet", "ockovani_pocet_davek", "nazev").from_statement(text(
        """
        select vakciny_prijate_pocet, ockovani_pocet_davek, om.nazev from ockovaci_mista_metriky omm
            join ockovaci_mista om on (omm.misto_id=om.id)
            where vakciny_prijate_pocet>10 and (ockovani_pocet_davek*1.0/vakciny_prijate_pocet<0.15)
            and omm.datum+'1 day'::interval>'{}'
        """.format(get_import_date())
    )).all()

    susp_vaccination_accepted = db.session.query("vakciny_prijate_pocet", "ockovani_pocet_davek",
                                                 "nazev").from_statement(text(
        """
        select vakciny_prijate_pocet, ockovani_pocet_davek, om.nazev from ockovaci_mista_metriky omm
            join ockovaci_mista om on (omm.misto_id=om.id)
            where vakciny_prijate_pocet>10 and (ockovani_pocet_davek*1.0/vakciny_prijate_pocet>2)
            and omm.datum+'1 day'::interval>'{}'
        """.format(get_import_date())
    )).all()

    susp_reservation_vaccination = db.session.query("nazev", "nrpzs_kod", "sum30_mimo_rezervace").from_statement(text(
        """
        select nazev, nrpzs_kod, sum( ockovani-pocet_rezervaci) sum30_mimo_rezervace
            from (
            select om.nazev, rez.nrpzs_kod, rez.datum, rez.pocet_rezervaci, ocko.ockovani, round(ockovani*1.0/pocet_rezervaci, 2) pomer from (
                        select ocm.nrpzs_kod, o.datum, sum(maximalni_kapacita-volna_kapacita) pocet_rezervaci 
                        from ockovani_rezervace o join ockovaci_mista ocm on (o.ockovaci_misto_id=ocm.id)
                        where import_id={} and o.datum<now() group by ocm.nrpzs_kod, o.datum) rez join (
                        select datum, zarizeni_kod, sum(pocet) ockovani from ockovani_lide 
                        group by datum, zarizeni_kod) ocko on (rez.nrpzs_kod=ocko.zarizeni_kod and rez.datum=ocko.datum)
                        join (select min(nazev) nazev, nrpzs_kod from ockovaci_mista group by nrpzs_kod) om on (om.nrpzs_kod=ocko.zarizeni_kod)
                        where pocet_rezervaci>0 and ockovani*1.0/pocet_rezervaci>=2
                        and rez.datum+'31 days'::interval>'{}' and ockovani>100
                        --order by round(ockovani*1.0/pocet_rezervaci, 2) desc
            ) pomery group by nazev, nrpzs_kod order by sum( ockovani-pocet_rezervaci) desc
        """.format(get_import_id(), get_import_date())
    )).all()

    susp_reservation_vaccination_low = db.session.query("nazev", "nrpzs_kod", "datum", "pocet_rezervaci", "ockovani",
                                                        "pomer").from_statement(text(
        """
        select om.nazev, rez.nrpzs_kod, rez.datum, rez.pocet_rezervaci, ocko.ockovani, round(ockovani*1.0/pocet_rezervaci, 2) pomer from (
            select ocm.nrpzs_kod, o.datum, sum(maximalni_kapacita-volna_kapacita) pocet_rezervaci 
            from ockovani_rezervace o join ockovaci_mista ocm on (o.ockovaci_misto_id=ocm.id)
            where import_id={} and o.datum<now() group by ocm.nrpzs_kod, o.datum) rez join (
            select datum, zarizeni_kod, sum(pocet) ockovani from ockovani_lide 
            group by datum, zarizeni_kod) ocko on (rez.nrpzs_kod=ocko.zarizeni_kod and rez.datum=ocko.datum)
            join (select min(nazev) nazev, nrpzs_kod from ockovaci_mista group by nrpzs_kod) om on (om.nrpzs_kod=ocko.zarizeni_kod)
            where pocet_rezervaci>100 and ockovani*1.0/pocet_rezervaci<0.3
            and rez.datum+'31 days'::interval>'{}'  
            order by round(ockovani*1.0/pocet_rezervaci, 2) desc
        """.format(get_import_id(), get_import_date())
    )).all()

    return render_template('dataquality.html', last_update=_last_import_modified(), now=_now(),
                           susp_vaccination_type=susp_vaccination_type,
                           vaccinated_age=susp_vaccination_age, susp_storage_vacc=susp_storage_vacc,
                           susp_vaccination=susp_vaccination,
                           susp_vaccination_accepted=susp_vaccination_accepted,
                           susp_reservation_vaccination=susp_reservation_vaccination,
                           susp_reservation_vaccination_low=susp_reservation_vaccination_low)


@bp.route("/report")
def report():
    # -- aktuální počet hospitalizovaných s covidem ve STR kraji
    current_hospital_kraje = db.session.query("nazev", "pocet_hospital").from_statement(text(
        """
        select k.nazev , sum(pocet_hosp) pocet_hospital
            from public.situace_orp so 
            join obce_orp oo on (so.orp_kod=oo.uzis_orp)
            join kraje k on (k.id=oo.kraj_nuts)
            where datum='{}' 
        group by k.nazev order by sum(pocet_hosp) desc; 	
        """.format(get_import_date())
    )).all()

    # -- přírůstek hospitalizovaných s covidem za posledních 7 dní ve STR kraji
    new_hospital_kraje = db.session.query("nazev", "nove_hosp_7").from_statement(text(
        """
        select k.nazev , sum(so.nove_hosp_7) nove_hosp_7
            from public.situace_orp so 
            join obce_orp oo on (so.orp_kod=oo.uzis_orp)
            join kraje k on (k.id=oo.kraj_nuts 
            )
            where datum='{}' 
        group by k.nazev
        order by sum(so.nove_hosp_7) desc; 	
        """.format(get_import_date())
    )).all()

    # -- aktuální počet potvrzených případů nákazy v kraji
    current_active_kraje = db.session.query("aktivni_pripady", "nazev").from_statement(text(
        """
        select sum(co.aktivni_pripady) aktivni_pripady, k.nazev from charakteristika_obci co
            join kraje k on (co.kraj_kod=k.id)
            where datum ='{}'
            group by k.nazev order by sum(co.aktivni_pripady) desc;
        """.format(get_import_date())
    )).all()

    # -- přírůstek potvrzených případů nákazy za posledních 14 dní v kraji
    new_14d_kraje = db.session.query("nove_pripady", "nazev").from_statement(text(
        """
        select sum(co.nove_pripady) nove_pripady, k.nazev from charakteristika_obci co
            join kraje k on (co.kraj_kod=k.id)
            where datum +'15 day'::interval> '{}' 
            group by k.nazev order by sum(co.nove_pripady) desc;
        """.format(get_import_date())
    )).all()

    # -- aktuální počet potvrzených případů nákazy podle okresů ve STR kraji
    current_cases_okres_kraje = db.session.query("aktivni_pripady", "okres_nazev", "kraj_nazev").from_statement(text(
        """
        select sum(co.aktivni_pripady) aktivni_pripady, o.nazev okres_nazev, k.nazev kraj_nazev from charakteristika_obci co
            join okresy o on (co.okres_kod=o.id)
            join kraje k on (co.kraj_kod=k.id)
            where datum  ='{}' 
        group by k.nazev, o.nazev order by k.nazev ,sum(co.aktivni_pripady) desc ;
        """.format(get_import_date())
    )).all()

    # -- přírůstek potvrzených případů nákazy za posledních 14 dní podle okresů v STR kraji
    new_14d_okres_kraje = db.session.query("nove_pripady_14_dni", "okres_nazev", "kraj_nazev").from_statement(text(
        """
        select sum(co.nove_pripady_14_dni) nove_pripady_14_dni, o.nazev okres_nazev, k.nazev kraj_nazev from charakteristika_obci co
            join okresy o on (co.okres_kod=o.id)
            join kraje k on (co.kraj_kod=k.id)
            where datum ='{}' 
        group by k.nazev , o.nazev order by k.nazev ,sum(co.aktivni_pripady) desc ;
        """.format(get_import_date())
    )).all()

    # -- 7denní incidence potvrzených případů nákazy na 100 000 obyvatel podle krajů
    incidence_7d_kraje = db.session.query("kraj_nazev", "incidence_7", "incidence_65_7",
                                          "incidence_75_7").from_statement(text(
        """         
        with pop as (select orp_kod kraj_nuts, sum(pocet) pocet from populace p where length(orp_kod)=5
        group by orp_kod)
        select round(incidence_7/(pop.pocet/100000),1) incidence_7, round(incidence_65_7/(pop.pocet/100000),1) incidence_65_7, 
            round(incidence_75_7/(pop.pocet/100000),1) incidence_75_7, kraj_nazev from 
        (
        select sum(incidence_7) incidence_7, sum(incidence_65_7) incidence_65_7, sum(incidence_75_7) incidence_75_7, 
            k.nazev kraj_nazev, k.id kraj_nuts
            from public.situace_orp so join obce_orp oo on (so.orp_kod=oo.uzis_orp)
            join kraje k on (k.id=oo.kraj_nuts)
            where datum='{}'
        group by k.nazev, k.id ) incidence join pop on (incidence.kraj_nuts=pop.kraj_nuts);
        """.format(get_import_date())
    )).all()

    return render_template('reporty.html', last_update=_last_import_modified(), now=_now(),
                           current_hospital_kraje=current_hospital_kraje,
                           new_hospital_kraje=new_hospital_kraje,
                           current_active_kraje=current_active_kraje,
                           new_14d_kraje=new_14d_kraje,
                           current_cases_okres_kraje=current_cases_okres_kraje,
                           new_14d_okres_kraje=new_14d_okres_kraje,
                           incidence_7d_kraje=incidence_7d_kraje
                           )


@bp.route("/praktici_admin")
def praktici_admin():
    if session.get('user_id') is not None and session.get('user_passwd') is not None:
        user = db.session.query(PrakticiLogin.zdravotnicke_zarizeni_kod, PrakticiLogin.heslo,
                                ZdravotnickeStredisko.nazev_cely) \
            .join(ZdravotnickeStredisko,
                  ZdravotnickeStredisko.zdravotnicke_zarizeni_kod == PrakticiLogin.zdravotnicke_zarizeni_kod) \
            .filter(PrakticiLogin.zdravotnicke_zarizeni_kod == session['user_id']) \
            .filter(PrakticiLogin.heslo == session['user_passwd']) \
            .one_or_none()
        user_vaccines = db.session.query(PrakticiKapacity) \
            .filter(PrakticiKapacity.zdravotnicke_zarizeni_kod == session['user_id']) \
            .order_by(PrakticiKapacity.typ_vakciny) \
            .all()
    else:
        user = None
        user_vaccines = None

    free_vaccines = queries.find_free_vaccines_available()

    vaccines_options = queries.find_free_vaccines_vaccine_options()

    kraj_options = queries.find_free_vaccines_kraj_options()

    return render_template('praktici_admin.html', last_update=_last_import_modified(), now=_now(), user=user,
                           user_vaccines=user_vaccines, all_vaccines=free_vaccines, vaccines_options=vaccines_options,
                           kraj_options=kraj_options)


@bp.route("/bezregistrace")
def bez_registrace():
    without_registration = db.session.query(OckovaciMistoBezRegistrace) \
        .order_by(OckovaciMistoBezRegistrace.kraj_kod, OckovaciMistoBezRegistrace.id) \
        .all()

    return render_template('bezregistrace.html', last_update=_last_import_modified(), now=_now(),
                           without_registration=without_registration)


def _last_import_modified():
    """
    Returns last successful import.
    """
    last_modified = db.session.query(func.max(Import.last_modified)) \
        .filter(Import.status == STATUS_FINISHED) \
        .first()[0]
    return 'nikdy' if last_modified is None else filters.format_datetime_short_wd(last_modified)


def _now():
    return datetime.now()
