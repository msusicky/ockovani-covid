from datetime import datetime

from flask import render_template, session
from sqlalchemy import func, text, column, and_, or_
from sqlalchemy.sql.functions import coalesce
from werkzeug.exceptions import abort

from app import db, bp, filters, queries
from app.context import get_import_date, STATUS_FINISHED
from app.models import Import, Okres, Kraj, OckovaciMisto, OckovaciMistoMetriky, KrajMetriky, OkresMetriky, CrMetriky, \
    PrakticiLogin, PrakticiKapacity, ZdravotnickeStredisko, OckovaciZarizeni, Vakcina


@bp.route('/')
def index():
    return render_template('index.html', last_update=_last_import_modified(), now=_now())


@bp.route("/mista")
def mista():
    mista = queries.find_centers(True, True)

    kraj_options = queries.find_kraj_options()

    third_doses_centers = queries.find_third_doses_centers()

    centers_vaccine_options = queries.find_centers_vaccine_options()

    return render_template('mista.html', last_update=_last_import_modified(), now=_now(), mista=mista,
                           kraj_options=kraj_options, third_doses_centers=third_doses_centers,
                           centers_vaccine_options=centers_vaccine_options)


@bp.route("/okres/<okres_name>")
def okres_detail(okres_name):
    okres = db.session.query(Okres).filter(Okres.nazev == okres_name).one_or_none()
    if okres is None:
        abort(404)

    mista = queries.find_centers(Okres.id, okres.id)

    third_doses_centers = queries.find_third_doses_centers()

    centers_vaccine_options = queries.find_centers_vaccine_options()

    doctors = queries.find_doctors(okres_id=okres.id)

    doctors_vaccine_options = queries.find_doctors_vaccine_options()

    free_vaccines = queries.find_free_vaccines_available(okres_id=okres.id)

    free_vaccines_illness_options = queries.find_free_vaccines_illness_options()

    metriky = db.session.query(OkresMetriky) \
        .filter(OkresMetriky.okres_id == okres.id, OkresMetriky.datum == get_import_date()) \
        .one_or_none()

    registrations = queries.count_registrations('okres_id', okres.id)

    return render_template('okres.html', last_update=_last_import_modified(), now=_now(), okres=okres, mista=mista,
                           third_doses_centers=third_doses_centers, centers_vaccine_options=centers_vaccine_options,
                           doctors=doctors, doctors_vaccine_options=doctors_vaccine_options,
                           free_vaccines=free_vaccines, free_vaccines_illness_options=free_vaccines_illness_options,
                           metriky=metriky, registrations=registrations)


@bp.route("/kraj/<kraj_name>")
def kraj_detail(kraj_name):
    kraj = db.session.query(Kraj).filter(Kraj.nazev_kratky == kraj_name).one_or_none()
    if kraj is None:
        abort(404)

    mista = queries.find_centers(Kraj.id, kraj.id)

    third_doses_centers = queries.find_third_doses_centers()

    centers_vaccine_options = queries.find_centers_vaccine_options()

    doctors = queries.find_doctors(kraj_id=kraj.id)

    doctors_vaccine_options = queries.find_doctors_vaccine_options()

    free_vaccines = queries.find_free_vaccines_available(kraj_id=kraj.id)

    free_vaccines_illness_options = queries.find_free_vaccines_illness_options()

    metriky = db.session.query(KrajMetriky) \
        .filter(KrajMetriky.kraj_id == kraj.id, KrajMetriky.datum == get_import_date()) \
        .one_or_none()

    registrations = queries.count_registrations('kraj_id', kraj.id)

    vaccines = queries.count_vaccines_kraj(kraj.id)

    vaccinated = queries.count_vaccinated(kraj.id)

    queue_graph_data = queries.get_queue_graph_data(kraj_id=kraj.id)

    return render_template('kraj.html', last_update=_last_import_modified(), now=_now(), kraj=kraj, mista=mista,
                           third_doses_centers=third_doses_centers, centers_vaccine_options=centers_vaccine_options,
                           doctors=doctors, doctors_vaccine_options=doctors_vaccine_options,
                           free_vaccines=free_vaccines, free_vaccines_illness_options=free_vaccines_illness_options,
                           metriky=metriky, vaccines=vaccines, registrations=registrations, vaccinated=vaccinated,
                           queue_graph_data=queue_graph_data)


@bp.route("/misto/<misto_id>")
def misto_detail(misto_id):
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
def mista_mapa():
    mista = queries.find_centers(True, True)

    third_doses_centers = queries.find_third_doses_centers()

    centers_vaccine_options = queries.find_centers_vaccine_options()

    return render_template('mista_mapa.html', last_update=_last_import_modified(), now=_now(), mista=mista,
                           third_doses_centers=third_doses_centers, centers_vaccine_options=centers_vaccine_options)


@bp.route("/praktici")
def praktici():
    doctors = queries.find_doctors()

    doctors_vaccine_options = queries.find_doctors_vaccine_options()

    kraj_options = queries.find_kraj_options()

    return render_template('praktici.html', last_update=_last_import_modified(), now=_now(), doctors=doctors,
                           doctors_vaccine_options=doctors_vaccine_options, kraj_options=kraj_options)


@bp.route("/praktici_mapa")
def praktici_mapa():
    doctors = queries.find_doctors_map()

    doctors_vaccine_options = queries.find_doctors_vaccine_options()

    return render_template('praktici_mapa.html', last_update=_last_import_modified(), now=_now(), doctors=doctors,
                           doctors_vaccine_options=doctors_vaccine_options)


@bp.route("/praktik/<nrpzs_kod>")
def praktik_detail(nrpzs_kod):
    doctor_offices = queries.find_doctor_offices(nrpzs_kod)
    if len(doctor_offices) == 0:
        abort(404)

    free_vaccines = queries.find_free_vaccines_available(nrpzs_kod=nrpzs_kod)

    return render_template('praktik.html', last_update=_last_import_modified(), now=_now(),
                           doctor_offices=doctor_offices, free_vaccines=free_vaccines)


@bp.route("/nabidky")
def nabidky():
    free_vaccines = queries.find_free_vaccines_available()

    free_vaccines_illness_options = queries.find_free_vaccines_illness_options()

    kraj_options = queries.find_kraj_options()

    return render_template('nabidky.html', last_update=_last_import_modified(), now=_now(),
                           free_vaccines=free_vaccines, free_vaccines_illness_options=free_vaccines_illness_options,
                           kraj_options=kraj_options)


@bp.route("/nabidky_mapa")
def nabidky_mapa():
    free_vaccines = queries.find_free_vaccines_available()

    free_vaccines_illness_options = queries.find_free_vaccines_illness_options()

    return render_template('nabidky_mapa.html', last_update=_last_import_modified(), now=_now(),
                           free_vaccines=free_vaccines, free_vaccines_illness_options=free_vaccines_illness_options)


@bp.route("/statistiky")
def statistiky():
    metriky = db.session.query(CrMetriky) \
        .filter(CrMetriky.datum == get_import_date()) \
        .one_or_none()

    eligible_count = queries.count_eligible()

    # interest = queries.count_interest()

    infected_orp_graph_data = queries.get_infected_orp_graph_data()

    tests_orp_graph_data = queries.get_tests_orp_graph_data()

    hospitalized_orp_graph_data = queries.get_hospitalized_orp_graph_data()

    vaccinated_orp_graph_data = queries.get_vaccinated_orp_graph_data()

    vaccinated_unvaccinated_comparison_age = queries.count_vaccinated_unvaccinated_comparison_age()
    vaccinated_unvaccinated_comparison_age_graph_data = vaccinated_unvaccinated_comparison_age[vaccinated_unvaccinated_comparison_age['vekova_skupina'] != '0-11']

    hospitalization_probabilities = queries.count_hospitalization_probabilities()

    vaccination_total_graph_data = queries.get_vaccination_total_graph_data()

    infected_graph_data = queries.get_infected_graph_data()

    deaths_graph_data = queries.get_deaths_graph_data()

    hospitalized_graph_data = queries.get_hospitalized_graph_data()

    tests_graph_data = queries.get_tests_graph_data()

    return render_template('statistiky.html', last_update=_last_import_modified(), now=_now(), metriky=metriky,
                           eligible_count=eligible_count, infected_orp_graph_data=infected_orp_graph_data,
                           tests_orp_graph_data=tests_orp_graph_data,
                           hospitalized_orp_graph_data=hospitalized_orp_graph_data,
                           vaccinated_orp_graph_data=vaccinated_orp_graph_data,
                           vaccinated_unvaccinated_comparison_age_graph_data=vaccinated_unvaccinated_comparison_age_graph_data,
                           hospitalization_probabilities=hospitalization_probabilities,
                           vaccination_total_graph_data=vaccination_total_graph_data,
                           infected_graph_data=infected_graph_data, deaths_graph_data=deaths_graph_data,
                           hospitalized_graph_data=hospitalized_graph_data, tests_graph_data=tests_graph_data)


@bp.route("/statistiky_ockovani")
def statistiky_ockovani():
    vaccinated = queries.count_vaccinated()

    vaccination_total_graph_data = queries.get_vaccination_total_graph_data()

    reservations_category = queries.count_reservations_category()

    vaccinated_category = queries.count_vaccinated_category()

    queue_graph_data = queries.get_queue_graph_data()

    registrations_graph_data = queries.get_registrations_graph_data()

    vaccinated_week = queries.count_vaccinated_week()

    top_centers = queries.count_top_centers()

    used_vaccine_graph_data = queries.get_used_vaccine_graph_data()

    received_vaccine_graph_data = queries.get_received_vaccine_graph_data()

    return render_template('statistiky_ockovani.html', last_update=_last_import_modified(), now=_now(),
                           vaccinated=vaccinated, vaccination_total_graph_data=vaccination_total_graph_data,
                           reservations_category=reservations_category, vaccinated_category=vaccinated_category,
                           queue_graph_data=queue_graph_data, registrations_graph_data=registrations_graph_data,
                           vaccinated_week=vaccinated_week, top_centers=top_centers,
                           used_vaccine_graph_data=used_vaccine_graph_data,
                           received_vaccine_graph_data=received_vaccine_graph_data)


@bp.route("/statistiky_srovnani")
def statistiky_srovnani():
    vaccinated_unvaccinated_comparison_age = queries.count_vaccinated_unvaccinated_comparison_age()

    vaccinated_unvaccinated_comparison_age_graph_data = vaccinated_unvaccinated_comparison_age[vaccinated_unvaccinated_comparison_age['vekova_skupina'] != '0-11']

    return render_template('statistiky_srovnani.html', last_update=_last_import_modified(), now=_now(),
                           vaccinated_unvaccinated_comparison_age=vaccinated_unvaccinated_comparison_age,
                           vaccinated_unvaccinated_comparison_age_graph_data=vaccinated_unvaccinated_comparison_age_graph_data)


@bp.route("/statistiky_nemocnice")
def statistiky_nemocnice():
    hospital_capacities_graph_data = queries.get_hospital_capacities_graph_data()

    return render_template('statistiky_nemocnice.html', last_update=_last_import_modified(), now=_now(),
                           hospital_capacities_graph_data=hospital_capacities_graph_data)


@bp.route("/napoveda")
def napoveda():
    return render_template('napoveda.html', last_update=_last_import_modified(), now=_now())


@bp.route("/odkazy")
def odkazy():
    return render_template('odkazy.html', last_update=_last_import_modified(), now=_now())


@bp.route("/dataquality")
def dataquality():
    susp_vaccination_type = db.session.query(column("datum"), column("vakcina"), column("zarizeni_kod"),
                                             column("zarizeni_nazev"), column("vekova_skupina"),
                                             column("pocet")).from_statement(text(
        """
        select datum, vakcina, zarizeni_kod, zarizeni_nazev, vekova_skupina, pocet 
        from ockovani_lide where vakcina not in ('Comirnaty','VAXZEVRIA','Spikevax', 'COVID-19 Vaccine Janssen')
        """
    )).all()

    susp_vaccination_age = db.session.query(column("datum"), column("vakcina"), column("zarizeni_kod"),
                                            column("zarizeni_nazev"), column("vekova_skupina"), column("pocet")
                                            ).from_statement(text(
        """
        select datum, vakcina, zarizeni_kod, zarizeni_nazev, vekova_skupina, pocet 
        from ockovani_lide where vakcina !='Comirnaty' and vekova_skupina='0-17'
        """
    )).all()

    susp_storage_vacc = db.session.query(column("pomer"), column("vakciny_skladem_pocet"),
                                         column("ockovani_pocet_davek"), column("nazev")).from_statement(text(
        """
        select ockovani_pocet_davek/vakciny_skladem_pocet pomer,vakciny_skladem_pocet, ockovani_pocet_davek, om.nazev from ockovaci_mista_metriky omm
            join ockovaci_mista om on (omm.misto_id=om.id)
            where vakciny_skladem_pocet>200 and (ockovani_pocet_davek*1.0/vakciny_skladem_pocet<0.15)
            and omm.datum+'2 day'::interval>'{}'
        """.format(get_import_date())
    )).all()

    susp_vaccination = db.session.query(column("vakciny_prijate_pocet"), column("ockovani_pocet_davek"),
                                        column("nazev")).from_statement(text(
        """
        select vakciny_prijate_pocet, ockovani_pocet_davek, om.nazev from ockovaci_mista_metriky omm
            join ockovaci_mista om on (omm.misto_id=om.id)
            where vakciny_prijate_pocet>10 and (ockovani_pocet_davek*1.0/vakciny_prijate_pocet<0.15)
            and omm.datum+'1 day'::interval>'{}'
        """.format(get_import_date())
    )).all()

    susp_vaccination_accepted = db.session.query(column("vakciny_prijate_pocet"), column("ockovani_pocet_davek"),
                                                 column("nazev")).from_statement(text(
        """
        select vakciny_prijate_pocet, ockovani_pocet_davek, om.nazev from ockovaci_mista_metriky omm
            join ockovaci_mista om on (omm.misto_id=om.id)
            where vakciny_prijate_pocet>10 and (ockovani_pocet_davek*1.0/vakciny_prijate_pocet>2)
            and omm.datum+'1 day'::interval>'{}'
        """.format(get_import_date())
    )).all()

    susp_reservation_vaccination = db.session.query(column("nazev"), column("nrpzs_kod"),
                                                    column("sum30_mimo_rezervace")).from_statement(text(
        """
        select nazev, nrpzs_kod, sum( ockovani-pocet_rezervaci) sum30_mimo_rezervace
            from (
            select om.nazev, rez.nrpzs_kod, rez.datum, rez.pocet_rezervaci, ocko.ockovani, round(ockovani*1.0/pocet_rezervaci, 2) pomer from (
                        select ocm.nrpzs_kod, o.datum, sum(maximalni_kapacita-volna_kapacita) pocet_rezervaci 
                        from ockovani_rezervace o join ockovaci_mista ocm on (o.ockovaci_misto_id=ocm.id)
                        where o.datum<now() group by ocm.nrpzs_kod, o.datum) rez join (
                        select datum, zarizeni_kod, sum(pocet) ockovani from ockovani_lide 
                        group by datum, zarizeni_kod) ocko on (rez.nrpzs_kod=ocko.zarizeni_kod and rez.datum=ocko.datum)
                        join (select min(nazev) nazev, nrpzs_kod from ockovaci_mista group by nrpzs_kod) om on (om.nrpzs_kod=ocko.zarizeni_kod)
                        where pocet_rezervaci>0 and ockovani*1.0/pocet_rezervaci>=2
                        and rez.datum+'31 days'::interval>'{}' and ockovani>100
                        --order by round(ockovani*1.0/pocet_rezervaci, 2) desc
            ) pomery group by nazev, nrpzs_kod order by sum( ockovani-pocet_rezervaci) desc
        """.format(get_import_date())
    )).all()

    susp_reservation_vaccination_low = db.session.query(column("nazev"), column("nrpzs_kod"), column("datum"),
                                                        column("pocet_rezervaci"), column("ockovani"),
                                                        column("pomer")).from_statement(text(
        """
        select om.nazev, rez.nrpzs_kod, rez.datum, rez.pocet_rezervaci, ocko.ockovani, round(ockovani*1.0/pocet_rezervaci, 2) pomer from (
            select ocm.nrpzs_kod, o.datum, sum(maximalni_kapacita-volna_kapacita) pocet_rezervaci 
            from ockovani_rezervace o join ockovaci_mista ocm on (o.ockovaci_misto_id=ocm.id)
            where o.datum<now() group by ocm.nrpzs_kod, o.datum) rez join (
            select datum, zarizeni_kod, sum(pocet) ockovani from ockovani_lide 
            group by datum, zarizeni_kod) ocko on (rez.nrpzs_kod=ocko.zarizeni_kod and rez.datum=ocko.datum)
            join (select min(nazev) nazev, nrpzs_kod from ockovaci_mista group by nrpzs_kod) om on (om.nrpzs_kod=ocko.zarizeni_kod)
            where pocet_rezervaci>100 and ockovani*1.0/pocet_rezervaci<0.3
            and rez.datum+'31 days'::interval>'{}'  
            order by round(ockovani*1.0/pocet_rezervaci, 2) desc
        """.format(get_import_date())
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
    current_hospital_kraje = db.session.query(column("nazev"), column("pocet_hospital")).from_statement(text(
        """
        select k.nazev, sum(pocet_hosp) pocet_hospital
            from public.situace_orp so 
            join obce_orp oo on (so.orp_kod=oo.uzis_orp)
            join kraje k on (k.id=oo.kraj_nuts)
            where datum='{}' 
        group by k.nazev order by sum(pocet_hosp) desc; 	
        """.format(get_import_date())
    )).all()

    # -- přírůstek hospitalizovaných s covidem za posledních 7 dní ve STR kraji
    new_hospital_kraje = db.session.query(column("nazev"), column("nove_hosp_7")).from_statement(text(
        """
        select k.nazev, sum(so.nove_hosp_7) nove_hosp_7
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
    current_active_kraje = db.session.query(column("aktivni_pripady"), column("nazev")).from_statement(text(
        """
        select sum(co.aktivni_pripady) aktivni_pripady, k.nazev from charakteristika_obci co
            join kraje k on (co.kraj_kod=k.id)
            where datum ='{}'
            group by k.nazev order by sum(co.aktivni_pripady) desc;
        """.format(get_import_date())
    )).all()

    # -- přírůstek potvrzených případů nákazy za posledních 14 dní v kraji
    new_14d_kraje = db.session.query(column("nove_pripady"), column("nazev")).from_statement(text(
        """
        select sum(co.nove_pripady) nove_pripady, k.nazev from charakteristika_obci co
            join kraje k on (co.kraj_kod=k.id)
            where datum +'15 day'::interval> '{}' 
            group by k.nazev order by sum(co.nove_pripady) desc;
        """.format(get_import_date())
    )).all()

    # -- aktuální počet potvrzených případů nákazy podle okresů ve STR kraji
    current_cases_okres_kraje = db.session.query(column("aktivni_pripady"), column("okres_nazev"),
                                                 column("kraj_nazev")).from_statement(text(
        """
        select sum(co.aktivni_pripady) aktivni_pripady, o.nazev okres_nazev, k.nazev kraj_nazev from charakteristika_obci co
            join okresy o on (co.okres_kod=o.id)
            join kraje k on (co.kraj_kod=k.id)
            where datum  ='{}' 
        group by k.nazev, o.nazev order by k.nazev ,sum(co.aktivni_pripady) desc ;
        """.format(get_import_date())
    )).all()

    # -- přírůstek potvrzených případů nákazy za posledních 14 dní podle okresů v STR kraji
    new_14d_okres_kraje = db.session.query(column("nove_pripady_14_dni"), column("okres_nazev"),
                                           column("kraj_nazev")).from_statement(text(
        """
        select sum(co.nove_pripady_14_dni) nove_pripady_14_dni, o.nazev okres_nazev, k.nazev kraj_nazev from charakteristika_obci co
            join okresy o on (co.okres_kod=o.id)
            join kraje k on (co.kraj_kod=k.id)
            where datum ='{}' 
        group by k.nazev , o.nazev order by k.nazev ,sum(co.aktivni_pripady) desc ;
        """.format(get_import_date())
    )).all()

    # -- 7denní incidence potvrzených případů nákazy na 100 000 obyvatel podle krajů
    incidence_7d_kraje = db.session.query(column("kraj_nazev"), column("incidence_7"), column("incidence_65_7"),
                                          column("incidence_75_7")).from_statement(text(
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
        user = db.session.query(PrakticiLogin.zdravotnicke_zarizeni_kod, PrakticiLogin.heslo, PrakticiLogin.neregistrovani,
                                coalesce(PrakticiLogin.telefon, ZdravotnickeStredisko.telefon).label('telefon'),
                                coalesce(PrakticiLogin.email, ZdravotnickeStredisko.email).label('email'),
                                ZdravotnickeStredisko.nazev_cely, ZdravotnickeStredisko.druh_zarizeni_kod) \
            .join(ZdravotnickeStredisko,
                  ZdravotnickeStredisko.zdravotnicke_zarizeni_kod == PrakticiLogin.zdravotnicke_zarizeni_kod) \
            .filter(PrakticiLogin.zdravotnicke_zarizeni_kod == session['user_id']) \
            .filter(PrakticiLogin.heslo == session['user_passwd']) \
            .one_or_none()
        user_vaccines = db.session.query(Vakcina.nemoc, Vakcina.vyrobce, PrakticiKapacity.aktivni,
                                         PrakticiKapacity.dospeli, PrakticiKapacity.deti, PrakticiKapacity.poznamka) \
            .outerjoin(PrakticiKapacity, and_(PrakticiKapacity.nemoc == Vakcina.nemoc,
                                              PrakticiKapacity.typ_vakciny == Vakcina.vyrobce,
                                              PrakticiKapacity.zdravotnicke_zarizeni_kod == session['user_id'])) \
            .filter(or_(PrakticiKapacity.zdravotnicke_zarizeni_kod == None,
                        PrakticiKapacity.zdravotnicke_zarizeni_kod == session['user_id'])) \
            .filter(Vakcina.aktivni == True) \
            .order_by(Vakcina.nemoc, Vakcina.vyrobce) \
            .all()
    else:
        user = None
        user_vaccines = None

    free_vaccines = queries.find_free_vaccines_available()

    free_vaccines_illness_options = queries.find_free_vaccines_illness_options()

    kraj_options = queries.find_kraj_options()

    return render_template('praktici_admin.html', last_update=_last_import_modified(), now=_now(), user=user,
                           user_vaccines=user_vaccines, all_vaccines=free_vaccines,
                           free_vaccines_illness_options=free_vaccines_illness_options, kraj_options=kraj_options)


@bp.route("/404")
def error_404():
    return render_template('error_404.html', last_update=_last_import_modified(), now=_now())


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
