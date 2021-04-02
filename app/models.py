from datetime import datetime

from sqlalchemy import Column, Integer, Unicode, DateTime, Boolean, Float, Date, ForeignKey, Index
from sqlalchemy.orm import relationship

from app import db


class Kraj(db.Model):
    __tablename__ = 'kraje'

    id = Column(Unicode, primary_key=True)
    nazev = Column(Unicode)


class Okres(db.Model):
    __tablename__ = 'okresy'

    id = Column(Unicode, primary_key=True)
    nazev = Column(Unicode)
    kraj_id = Column(Unicode, ForeignKey('kraje.id'))

    kraj = relationship("Kraj", back_populates="okresy")

    def __repr__(self):
        return "<Okres(nazev='%s')>" % self.nazev


Kraj.okresy = relationship("Okres", back_populates="kraj")


class ObceORP(db.Model):
    __tablename__ = 'obce_orp'

    kod_obce_orp = Column(Unicode, primary_key=True)
    nazev_obce = Column(Unicode)
    okres_nuts = Column(Unicode)
    kraj_nuts = Column(Unicode, ForeignKey('kraje.id'))
    aken = Column(Unicode, ForeignKey('okresy.id'))
    uzis_orp = Column(Unicode)

    kraj = relationship("Kraj", back_populates="kraje_orp")
    okres = relationship("Okres", back_populates="okresy_orp")

    def __repr__(self):
        return "<ObceORP(kod_obce_orp='%s', nazev_obce='%s')>" % self.kod_obce_orp, self.nazev_obce


Kraj.kraje_orp = relationship("ObceORP", back_populates="kraj")
Okres.okresy_orp = relationship("ObceORP", back_populates="okres")


class Populace(db.Model):
    __tablename__ = 'populace'

    orp_kod = Column(Unicode, primary_key=True)
    pocet = Column(Integer, primary_key=True)
    vek = Column(Integer, primary_key=True)

    def __repr__(self):
        return "<Populace(orp_kod='%s', pocet=%s, vek=%s)>" % (
            self.orp_kod, self.pocet, self.vek)


class PopulaceKategorie(db.Model):
    __tablename__ = 'populace_kategorie'

    vekova_skupina = Column(Unicode, primary_key=True)
    min_vek = Column(Integer)
    max_vek = Column(Integer)

    def __repr__(self):
        return "<PopulaceKategorie(vekova_skupina='%s', min_vek=%s, max_vek=%s)>" % (
            self.vekova_skupina, self.min_vek, self.max_vek)


class OckovaciMisto(db.Model):
    __tablename__ = 'ockovaci_mista'

    id = Column(Unicode, primary_key=True)
    nazev = Column(Unicode)
    okres_id = Column(Unicode, ForeignKey('okresy.id'))
    status = Column(Boolean)
    adresa = Column(Unicode)
    latitude = Column(Float)
    longitude = Column(Float)
    nrpzs_kod = Column(Unicode, index=True)
    minimalni_kapacita = Column(Integer)
    bezbarierovy_pristup = Column(Boolean)
    service_id = Column(Integer)
    operation_id = Column(Integer)
    odkaz = Column(Unicode)

    okres = relationship("Okres", back_populates="ockovaci_mista")

    def __repr__(self):
        return "<OckovaciMisto(nazev='%s', service_id=%s, operation_id=%s)>" % (
            self.nazev, self.service_id, self.operation_id)


Okres.ockovaci_mista = relationship("OckovaciMisto", back_populates="okres")


class Import(db.Model):
    __tablename__ = 'importy'

    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True)
    start = Column(DateTime, default=datetime.now())
    end = Column(DateTime)
    last_modified = Column(DateTime)
    status = Column(Unicode)

    def __repr__(self):
        return "<Import(id=%s, start='%s', status='%s')>" % (self.id, self.start, self.status)


class OckovaniSpotreba(db.Model):
    __tablename__ = 'ockovani_spotreba'

    datum = Column(Date, primary_key=True)
    ockovaci_misto_id = Column(Unicode, ForeignKey('ockovaci_mista.id'), primary_key=True)
    ockovaci_latka = Column(Unicode, primary_key=True)
    vyrobce = Column(Unicode)
    pouzite_ampulky = Column(Integer)
    znehodnocene_ampulky = Column(Integer)
    pouzite_davky = Column(Integer)
    znehodnocene_davky = Column(Integer)

    misto = relationship('OckovaciMisto', back_populates='ockovani_spotreba')

    def __repr__(self):
        return "<OckovaniSpotreba(ockovaci_misto_id='%s', datum='%s', ockovaci_latka=%s, pouzite_ampulky=%s)>" % (
            self.ockovaci_misto_id, self.datum, self.ockovaci_latka, self.pouzite_ampulky)


OckovaciMisto.ockovani_spotreba = relationship("OckovaniSpotreba", back_populates="misto")


class OckovaniDistribuce(db.Model):
    __tablename__ = 'ockovani_distribuce'

    datum = Column(Date, primary_key=True)
    ockovaci_misto_id = Column(Unicode, ForeignKey('ockovaci_mista.id'), primary_key=True, index=True)
    cilove_ockovaci_misto_id = Column(Unicode, primary_key=True, index=True)
    ockovaci_latka = Column(Unicode, primary_key=True)
    vyrobce = Column(Unicode)
    akce = Column(Unicode, primary_key=True)
    pocet_ampulek = Column(Integer)
    pocet_davek = Column(Integer)

    misto = relationship('OckovaciMisto', back_populates='ockovani_distribuce')

    def __repr__(self):
        return "<OckovaniDistribuce(ockovaci_misto_id='%s', cilove_ockovaci_misto_id='%s', datum='%s', ockovaci_latka='%s', pocet_ampulek=%s)>" % (
            self.ockovaci_misto_id, self.cilove_ockovaci_misto_id, self.datum, self.ockovaci_latka, self.pocet_ampulek)


OckovaciMisto.ockovani_distribuce = relationship("OckovaniDistribuce", back_populates="misto")


class OckovaniLide(db.Model):
    __tablename__ = 'ockovani_lide'

    datum = Column(Date, primary_key=True)
    vakcina = Column(Unicode, primary_key=True)
    kraj_nuts_kod = Column(Unicode, index=True)
    kraj_nazev = Column(Unicode)
    zarizeni_kod = Column(Unicode, primary_key=True, index=True)
    zarizeni_nazev = Column(Unicode)
    poradi_davky = Column(Integer, primary_key=True)
    vekova_skupina = Column(Unicode, primary_key=True)
    pocet = Column(Integer)

    def __repr__(self):
        return "<OckovaniLide(zarizeni_nazev='%s', vakcina='%s', datum='%s', poradi_davky=%s, vekova_skupina='%s', pocet=%s)>" % (
            self.zarizeni_nazev, self.vakcina, self.datum, self.poradi_davky, self.vekova_skupina, self.pocet)


class OckovaniLideProfese(db.Model):
    __tablename__ = 'ockovani_lide_profese'

    datum = Column(Date, primary_key=True)
    vakcina = Column(Unicode, primary_key=True)
    kraj_nuts_kod = Column(Unicode, index=True)
    zarizeni_kod = Column(Unicode, primary_key=True, index=True)
    poradi_davky = Column(Integer, primary_key=True)
    vekova_skupina = Column(Unicode, primary_key=True)
    kraj_bydl_nuts = Column(Unicode, primary_key=True, index=True)
    indikace_zdravotnik = Column(Boolean, primary_key=True)
    indikace_socialni_sluzby = Column(Boolean, primary_key=True)
    indikace_ostatni = Column(Boolean, primary_key=True)
    indikace_pedagog = Column(Boolean, primary_key=True)
    indikace_skolstvi_ostatni = Column(Boolean, primary_key=True)
    pocet = Column(Integer)

    def __repr__(self):
        return "<OckovaniLideProfese(zarizeni_kod='%s', vakcina='%s', datum='%s', poradi_davky=%s, vekova_skupina='%s', pocet=%s)>" % (
            self.zarizeni_kod, self.vakcina, self.datum, self.poradi_davky, self.vekova_skupina, self.pocet)


class OckovaniRegistrace(db.Model):
    __tablename__ = 'ockovani_registrace'

    datum = Column(Date, primary_key=True)
    ockovaci_misto_id = Column(Unicode, ForeignKey('ockovaci_mista.id'), primary_key=True)
    vekova_skupina = Column(Unicode, primary_key=True)
    povolani = Column(Unicode, primary_key=True)
    stat = Column(Unicode, primary_key=True)
    rezervace = Column(Boolean, primary_key=True)
    datum_rezervace = Column(Date, primary_key=True)
    pocet = Column(Integer)
    import_id = Column(Integer, ForeignKey('importy.id', ondelete='CASCADE'), primary_key=True)

    import_ = relationship('Import', back_populates='ockovani_registrace')
    misto = relationship('OckovaciMisto', back_populates='ockovani_registrace')

    def __repr__(self):
        return "<OckovaniRegistrace(ockovaci_misto_id='%s', datum='%s', povolani='%s', vekova_skupina='%s', datum_rezervace='%s', pocet=%s)>" % (
            self.ockovaci_misto_id, self.datum, self.povolani, self.vekova_skupina, self.datum_rezervace, self.pocet)


Import.ockovani_registrace = relationship("OckovaniRegistrace", back_populates="import_", cascade="delete")
OckovaciMisto.ockovani_registrace = relationship("OckovaniRegistrace", back_populates="misto")


class OckovaniRezervace(db.Model):
    __tablename__ = 'ockovani_rezervace'

    datum = Column(Date, primary_key=True)
    ockovaci_misto_id = Column(Unicode, ForeignKey('ockovaci_mista.id'), primary_key=True)
    volna_kapacita = Column(Integer)
    maximalni_kapacita = Column(Integer)
    kalendar_ockovani = Column(Unicode, primary_key=True)
    import_id = Column(Integer, ForeignKey('importy.id', ondelete='CASCADE'), primary_key=True)

    import_ = relationship('Import', back_populates='ockovani_rezervace')
    misto = relationship('OckovaciMisto', back_populates='ockovani_rezervace')

    def __repr__(self):
        return "<OckovaniRezervace(ockovaci_misto_id='%s', datum='%s', volna_kapacita='%s', kalendar_ockovani='%s')>" % (
            self.ockovaci_misto_id, self.datum, self.volna_kapacita, self.kalendar_ockovani)


Import.ockovani_rezervace = relationship("OckovaniRezervace", back_populates="import_", cascade="delete")
OckovaciMisto.ockovani_rezervace = relationship("OckovaniRezervace", back_populates="misto")


class ZdravotnickeStredisko(db.Model):
    __tablename__ = 'zdravotnicke_stredisko'

    zdravotnicke_zarizeni_id = Column(Integer, primary_key=True)
    pcz = Column(Integer)
    pcdp = Column(Integer)
    nazev_cely = Column(Unicode)
    zdravotnicke_zarizeni_kod = Column(Unicode)
    druh_zarizeni_kod = Column(Integer)
    druh_zarizeni = Column(Unicode)
    obec = Column(Unicode)
    psc = Column(Unicode)
    ulice = Column(Unicode)
    cislo_domu = Column(Unicode)
    kraj = Column(Unicode)
    kraj_kod = Column(Unicode)
    okres = Column(Unicode)
    okres_kod = Column(Unicode)
    nrpzs_kod = Column(Unicode)


class KrajMetriky(db.Model):
    __tablename__ = 'kraje_metriky'

    kraj_id = Column(Unicode, ForeignKey('kraje.id'), primary_key=True)
    datum = Column(DateTime, primary_key=True)
    pocet_obyvatel_celkem = Column(Integer)
    pocet_obyvatel_dospeli = Column(Integer)
    rezervace_celkem = Column(Integer)                          # pocet vsech rezervaci (vsechny kalendare)
    rezervace_celkem_zmena_den = Column(Integer)                # pocet vsech rezervaci (vsechny kalendare) - zmena za den
    rezervace_celkem_zmena_tyden = Column(Integer)              # pocet vsech rezervaci (vsechny kalendare) - zmena za tyden
    rezervace_cekajici = Column(Integer)                        # pocet rezervaci cekajicich na ockovani (vsechny kalendare)
    rezervace_cekajici_zmena_den = Column(Integer)              # pocet rezervaci cekajicich na ockovani (vsechny kalendare) - zmena za den
    rezervace_cekajici_zmena_tyden = Column(Integer)            # pocet rezervaci cekajicich na ockovani (vsechny kalendare) - zmena za tyden
    rezervace_cekajici_1 = Column(Integer)                      # pocet rezervaci cekajicich na ockovani (kalendar pro 1. davky)
    rezervace_cekajici_1_zmena_den = Column(Integer)            # pocet rezervaci cekajicich na ockovani (kalendar pro 1. davky) - zmena za den
    rezervace_cekajici_1_zmena_tyden = Column(Integer)          # pocet rezervaci cekajicich na ockovani (kalendar pro 1. davky) - zmena za tyden
    rezervace_cekajici_2 = Column(Integer)                      # pocet rezervaci cekajicich na ockovani (kalendar pro 2. davky)
    rezervace_cekajici_2_zmena_den = Column(Integer)            # pocet rezervaci cekajicich na ockovani (kalendar pro 2. davky) - zmena za den
    rezervace_cekajici_2_zmena_tyden = Column(Integer)          # pocet rezervaci cekajicich na ockovani (kalendar pro 2. davky) - zmena za tyden
    rezervace_kapacita = Column(Integer)                        # kapacita na aktualni den (vsechny kalendare)
    rezervace_kapacita_zmena_den = Column(Integer)              # kapacita na aktualni den (vsechny kalendare) - zmena za den
    rezervace_kapacita_zmena_tyden = Column(Integer)            # kapacita na aktualni den (vsechny kalendare) - zmena za tyden
    rezervace_kapacita_1 = Column(Integer)                      # kapacita na aktualni den (kalendar pro 1. davky)
    rezervace_kapacita_1_zmena_den = Column(Integer)            # kapacita na aktualni den (kalendar pro 1. davky) - zmena za den
    rezervace_kapacita_1_zmena_tyden = Column(Integer)          # kapacita na aktualni den (kalendar pro 1. davky) - zmena za tyden
    rezervace_kapacita_2 = Column(Integer)                      # kapacita na aktualni den (kalendar pro 2. davky)
    rezervace_kapacita_2_zmena_den = Column(Integer)            # kapacita na aktualni den (kalendar pro 2. davky) - zmena za den
    rezervace_kapacita_2_zmena_tyden = Column(Integer)          # kapacita na aktualni den (kalendar pro 2. davky) - zmena za tyden
    rezervace_nejblizsi_volno = Column(Date)                    # nejblizsi den s volnym mistem
    registrace_celkem = Column(Integer)                         # pocet vsech registraci
    registrace_celkem_zmena_den = Column(Integer)               # pocet vsech registraci - zmena za den
    registrace_celkem_zmena_tyden = Column(Integer)             # pocet vsech registraci - zmena za tyden
    registrace_fronta = Column(Integer)                         # pocet registraci bez rezervace
    registrace_fronta_zmena_den = Column(Integer)               # pocet registraci bez rezervace - zmena za den
    registrace_fronta_zmena_tyden = Column(Integer)             # pocet registraci bez rezervace - zmena za tyden
    registrace_tydenni_uspesnost = Column(Float)                # uspesnost rezervaci za poslednich 7 dni
    registrace_tydenni_uspesnost_zmena_den = Column(Float)      # uspesnost rezervaci za poslednich 7 dni - zmena za den
    registrace_tydenni_uspesnost_zmena_tyden = Column(Float)    # uspesnost rezervaci za poslednich 7 dni - zmena za tyden
    registrace_14denni_uspesnost = Column(Float)                # uspesnost rezervaci za poslednich 14 dni
    registrace_14denni_uspesnost_zmena_den = Column(Float)      # uspesnost rezervaci za poslednich 14 dni - zmena za den
    registrace_14denni_uspesnost_zmena_tyden = Column(Float)    # uspesnost rezervaci za poslednich 14 dni - zmena za tyden
    registrace_30denni_uspesnost = Column(Float)                # uspesnost rezervaci za poslednich 30 dni
    registrace_30denni_uspesnost_zmena_den = Column(Float)      # uspesnost rezervaci za poslednich 30 dni - zmena za den
    registrace_30denni_uspesnost_zmena_tyden = Column(Float)    # uspesnost rezervaci za poslednich 30 dni - zmena za tyden
    registrace_prumer_cekani = Column(Float)                    # prumerna doba cekani na rezervaci z poslednich 7 dni
    registrace_prumer_cekani_zmena_den = Column(Float)          # prumerna doba cekani na rezervaci z poslednich 7 dni - zmena za den
    registrace_prumer_cekani_zmena_tyden = Column(Float)        # prumerna doba cekani na rezervaci z poslednich 7 dni - zmena za tyden
    registrace_fronta_prumer_cekani = Column(Float)             # prumerna doba ve fronte
    registrace_fronta_prumer_cekani_zmena_den = Column(Float)   # prumerna doba ve fronte - zmena za den
    registrace_fronta_prumer_cekani_zmena_tyden = Column(Float) # prumerna doba ve fronte - zmena za tyden
    ockovani_pocet_davek = Column(Integer)                      # pocet ockovanych davek
    ockovani_pocet_davek_zmena_den = Column(Integer)            # pocet ockovanych davek - zmena za den
    ockovani_pocet_davek_zmena_tyden = Column(Integer)          # pocet ockovanych davek - zmena za tyden
    ockovani_pocet_castecne = Column(Integer)                   # pocet ockovanych alespon castecne
    ockovani_pocet_castecne_zmena_den = Column(Integer)         # pocet ockovanych alespon castecne - zmena za den
    ockovani_pocet_castecne_zmena_tyden = Column(Integer)       # pocet ockovanych alespon castecne - zmena za tyden
    ockovani_pocet_plne = Column(Integer)                       # pocet ockovanych plne (vsechny davky)
    ockovani_pocet_plne_zmena_den = Column(Integer)             # pocet ockovanych plne (vsechny davky) - zmena za den
    ockovani_pocet_plne_zmena_tyden = Column(Integer)           # pocet ockovanych plne (vsechny davky) - zmena za tyden
    vakciny_prijate_pocet = Column(Integer)                     # pocet prijatych vakcin
    vakciny_prijate_pocet_zmena_den = Column(Integer)           # pocet prijatych vakcin - zmena za den
    vakciny_prijate_pocet_zmena_tyden = Column(Integer)         # pocet prijatych vakcin - zmena za tyden
    vakciny_ockovane_pocet = Column(Integer)                    # pocet ockovanych vakcin
    vakciny_ockovane_pocet_zmena_den = Column(Integer)          # pocet ockovanych vakcin - zmena za den
    vakciny_ockovane_pocet_zmena_tyden = Column(Integer)        # pocet ockovanych vakcin - zmena za tyden
    vakciny_znicene_pocet = Column(Integer)                     # pocet znicenych vakcin
    vakciny_znicene_pocet_zmena_den = Column(Integer)           # pocet znicenych vakcin - zmena za den
    vakciny_znicene_pocet_zmena_tyden = Column(Integer)         # pocet znicenych vakcin - zmena za tyden
    vakciny_skladem_pocet = Column(Integer)                     # odhad vakcin skladem
    vakciny_skladem_pocet_zmena_den = Column(Integer)           # odhad vakcin skladem - zmena za den
    vakciny_skladem_pocet_zmena_tyden = Column(Integer)         # odhad vakcin skladem - zmena za tyden

    kraj = relationship("Kraj", back_populates="metriky")

    def __repr__(self):
        return "<KrajMetriky(id='%s', datum='%s')>" % (self.kraj_id, self.datum)


Kraj.metriky = relationship("KrajMetriky", back_populates="kraj")
Index('idx_kraj_id_datum', KrajMetriky.kraj_id, KrajMetriky.datum)

class OkresMetriky(db.Model):
    __tablename__ = 'okresy_metriky'

    okres_id = Column(Unicode, ForeignKey('okresy.id'), primary_key=True)
    datum = Column(DateTime, primary_key=True)
    pocet_obyvatel_celkem = Column(Integer)
    pocet_obyvatel_dospeli = Column(Integer)
    rezervace_celkem = Column(Integer)                          # pocet vsech rezervaci (vsechny kalendare)
    rezervace_celkem_zmena_den = Column(Integer)                # pocet vsech rezervaci (vsechny kalendare) - zmena za den
    rezervace_celkem_zmena_tyden = Column(Integer)              # pocet vsech rezervaci (vsechny kalendare) - zmena za tyden
    rezervace_cekajici = Column(Integer)                        # pocet rezervaci cekajicich na ockovani (vsechny kalendare)
    rezervace_cekajici_zmena_den = Column(Integer)              # pocet rezervaci cekajicich na ockovani (vsechny kalendare) - zmena za den
    rezervace_cekajici_zmena_tyden = Column(Integer)            # pocet rezervaci cekajicich na ockovani (vsechny kalendare) - zmena za tyden
    rezervace_cekajici_1 = Column(Integer)                      # pocet rezervaci cekajicich na ockovani (kalendar pro 1. davky)
    rezervace_cekajici_1_zmena_den = Column(Integer)            # pocet rezervaci cekajicich na ockovani (kalendar pro 1. davky) - zmena za den
    rezervace_cekajici_1_zmena_tyden = Column(Integer)          # pocet rezervaci cekajicich na ockovani (kalendar pro 1. davky) - zmena za tyden
    rezervace_cekajici_2 = Column(Integer)                      # pocet rezervaci cekajicich na ockovani (kalendar pro 2. davky)
    rezervace_cekajici_2_zmena_den = Column(Integer)            # pocet rezervaci cekajicich na ockovani (kalendar pro 2. davky) - zmena za den
    rezervace_cekajici_2_zmena_tyden = Column(Integer)          # pocet rezervaci cekajicich na ockovani (kalendar pro 2. davky) - zmena za tyden
    rezervace_kapacita = Column(Integer)                        # kapacita na aktualni den (vsechny kalendare)
    rezervace_kapacita_zmena_den = Column(Integer)              # kapacita na aktualni den (vsechny kalendare) - zmena za den
    rezervace_kapacita_zmena_tyden = Column(Integer)            # kapacita na aktualni den (vsechny kalendare) - zmena za tyden
    rezervace_kapacita_1 = Column(Integer)                      # kapacita na aktualni den (kalendar pro 1. davky)
    rezervace_kapacita_1_zmena_den = Column(Integer)            # kapacita na aktualni den (kalendar pro 1. davky) - zmena za den
    rezervace_kapacita_1_zmena_tyden = Column(Integer)          # kapacita na aktualni den (kalendar pro 1. davky) - zmena za tyden
    rezervace_kapacita_2 = Column(Integer)                      # kapacita na aktualni den (kalendar pro 2. davky)
    rezervace_kapacita_2_zmena_den = Column(Integer)            # kapacita na aktualni den (kalendar pro 2. davky) - zmena za den
    rezervace_kapacita_2_zmena_tyden = Column(Integer)          # kapacita na aktualni den (kalendar pro 2. davky) - zmena za tyden
    rezervace_nejblizsi_volno = Column(Date)                    # nejblizsi den s volnym mistem
    registrace_celkem = Column(Integer)                         # pocet vsech registraci
    registrace_celkem_zmena_den = Column(Integer)               # pocet vsech registraci - zmena za den
    registrace_celkem_zmena_tyden = Column(Integer)             # pocet vsech registraci - zmena za tyden
    registrace_fronta = Column(Integer)                         # pocet registraci bez rezervace
    registrace_fronta_zmena_den = Column(Integer)               # pocet registraci bez rezervace - zmena za den
    registrace_fronta_zmena_tyden = Column(Integer)             # pocet registraci bez rezervace - zmena za tyden
    registrace_tydenni_uspesnost = Column(Float)                # uspesnost rezervaci za poslednich 7 dni
    registrace_tydenni_uspesnost_zmena_den = Column(Float)      # uspesnost rezervaci za poslednich 7 dni - zmena za den
    registrace_tydenni_uspesnost_zmena_tyden = Column(Float)    # uspesnost rezervaci za poslednich 7 dni - zmena za tyden
    registrace_14denni_uspesnost = Column(Float)                # uspesnost rezervaci za poslednich 14 dni
    registrace_14denni_uspesnost_zmena_den = Column(Float)      # uspesnost rezervaci za poslednich 14 dni - zmena za den
    registrace_14denni_uspesnost_zmena_tyden = Column(Float)    # uspesnost rezervaci za poslednich 14 dni - zmena za tyden
    registrace_30denni_uspesnost = Column(Float)                # uspesnost rezervaci za poslednich 30 dni
    registrace_30denni_uspesnost_zmena_den = Column(Float)      # uspesnost rezervaci za poslednich 30 dni - zmena za den
    registrace_30denni_uspesnost_zmena_tyden = Column(Float)    # uspesnost rezervaci za poslednich 30 dni - zmena za tyden
    registrace_prumer_cekani = Column(Float)                    # prumerna doba cekani na rezervaci z poslednich 7 dni
    registrace_prumer_cekani_zmena_den = Column(Float)          # prumerna doba cekani na rezervaci z poslednich 7 dni - zmena za den
    registrace_prumer_cekani_zmena_tyden = Column(Float)        # prumerna doba cekani na rezervaci z poslednich 7 dni - zmena za tyden
    registrace_fronta_prumer_cekani = Column(Float)             # prumerna doba ve fronte
    registrace_fronta_prumer_cekani_zmena_den = Column(Float)   # prumerna doba ve fronte - zmena za den
    registrace_fronta_prumer_cekani_zmena_tyden = Column(Float) # prumerna doba ve fronte - zmena za tyden
    vakciny_prijate_pocet = Column(Integer)                     # pocet prijatych vakcin
    vakciny_prijate_pocet_zmena_den = Column(Integer)           # pocet prijatych vakcin - zmena za den
    vakciny_prijate_pocet_zmena_tyden = Column(Integer)         # pocet prijatych vakcin - zmena za tyden
    vakciny_ockovane_pocet = Column(Integer)                    # pocet ockovanych vakcin
    vakciny_ockovane_pocet_zmena_den = Column(Integer)          # pocet ockovanych vakcin - zmena za den
    vakciny_ockovane_pocet_zmena_tyden = Column(Integer)        # pocet ockovanych vakcin - zmena za tyden
    vakciny_znicene_pocet = Column(Integer)                     # pocet znicenych vakcin
    vakciny_znicene_pocet_zmena_den = Column(Integer)           # pocet znicenych vakcin - zmena za den
    vakciny_znicene_pocet_zmena_tyden = Column(Integer)         # pocet znicenych vakcin - zmena za tyden

    okres = relationship("Okres", back_populates="metriky")

    def __repr__(self):
        return "<OkresMetriky(id='%s', datum='%s')>" % (self.id, self.datum)


Okres.metriky = relationship("OkresMetriky", back_populates="okres")
Index('idx_okres_id_datum', OkresMetriky.okres_id, OkresMetriky.datum)

class OckovaciMistoMetriky(db.Model):
    __tablename__ = 'ockovaci_mista_metriky'

    misto_id = Column(Unicode, ForeignKey('ockovaci_mista.id'), primary_key=True)
    datum = Column(DateTime, primary_key=True)
    rezervace_celkem = Column(Integer)                          # pocet vsech rezervaci (vsechny kalendare)
    rezervace_celkem_zmena_den = Column(Integer)                # pocet vsech rezervaci (vsechny kalendare) - zmena za den
    rezervace_celkem_zmena_tyden = Column(Integer)              # pocet vsech rezervaci (vsechny kalendare) - zmena za tyden
    rezervace_cekajici = Column(Integer)                        # pocet rezervaci cekajicich na ockovani (vsechny kalendare)
    rezervace_cekajici_zmena_den = Column(Integer)              # pocet rezervaci cekajicich na ockovani (vsechny kalendare) - zmena za den
    rezervace_cekajici_zmena_tyden = Column(Integer)            # pocet rezervaci cekajicich na ockovani (vsechny kalendare) - zmena za tyden
    rezervace_cekajici_1 = Column(Integer)                      # pocet rezervaci cekajicich na ockovani (kalendar pro 1. davky)
    rezervace_cekajici_1_zmena_den = Column(Integer)            # pocet rezervaci cekajicich na ockovani (kalendar pro 1. davky) - zmena za den
    rezervace_cekajici_1_zmena_tyden = Column(Integer)          # pocet rezervaci cekajicich na ockovani (kalendar pro 1. davky) - zmena za tyden
    rezervace_cekajici_2 = Column(Integer)                      # pocet rezervaci cekajicich na ockovani (kalendar pro 2. davky)
    rezervace_cekajici_2_zmena_den = Column(Integer)            # pocet rezervaci cekajicich na ockovani (kalendar pro 2. davky) - zmena za den
    rezervace_cekajici_2_zmena_tyden = Column(Integer)          # pocet rezervaci cekajicich na ockovani (kalendar pro 2. davky) - zmena za tyden
    rezervace_kapacita = Column(Integer)                        # kapacita na aktualni den (vsechny kalendare)
    rezervace_kapacita_zmena_den = Column(Integer)              # kapacita na aktualni den (vsechny kalendare) - zmena za den
    rezervace_kapacita_zmena_tyden = Column(Integer)            # kapacita na aktualni den (vsechny kalendare) - zmena za tyden
    rezervace_kapacita_1 = Column(Integer)                      # kapacita na aktualni den (kalendar pro 1. davky)
    rezervace_kapacita_1_zmena_den = Column(Integer)            # kapacita na aktualni den (kalendar pro 1. davky) - zmena za den
    rezervace_kapacita_1_zmena_tyden = Column(Integer)          # kapacita na aktualni den (kalendar pro 1. davky) - zmena za tyden
    rezervace_kapacita_2 = Column(Integer)                      # kapacita na aktualni den (kalendar pro 2. davky)
    rezervace_kapacita_2_zmena_den = Column(Integer)            # kapacita na aktualni den (kalendar pro 2. davky) - zmena za den
    rezervace_kapacita_2_zmena_tyden = Column(Integer)          # kapacita na aktualni den (kalendar pro 2. davky) - zmena za tyden
    rezervace_nejblizsi_volno = Column(Date)                    # nejblizsi den s volnym mistem
    registrace_celkem = Column(Integer)                         # pocet vsech registraci
    registrace_celkem_zmena_den = Column(Integer)               # pocet vsech registraci - zmena za den
    registrace_celkem_zmena_tyden = Column(Integer)             # pocet vsech registraci - zmena za tyden
    registrace_fronta = Column(Integer)                         # pocet registraci bez rezervace
    registrace_fronta_zmena_den = Column(Integer)               # pocet registraci bez rezervace - zmena za den
    registrace_fronta_zmena_tyden = Column(Integer)             # pocet registraci bez rezervace - zmena za tyden
    registrace_tydenni_uspesnost = Column(Float)                # uspesnost rezervaci za poslednich 7 dni
    registrace_tydenni_uspesnost_zmena_den = Column(Float)      # uspesnost rezervaci za poslednich 7 dni - zmena za den
    registrace_tydenni_uspesnost_zmena_tyden = Column(Float)    # uspesnost rezervaci za poslednich 7 dni - zmena za tyden
    registrace_14denni_uspesnost = Column(Float)                # uspesnost rezervaci za poslednich 14 dni
    registrace_14denni_uspesnost_zmena_den = Column(Float)      # uspesnost rezervaci za poslednich 14 dni - zmena za den
    registrace_14denni_uspesnost_zmena_tyden = Column(Float)    # uspesnost rezervaci za poslednich 14 dni - zmena za tyden
    registrace_30denni_uspesnost = Column(Float)                # uspesnost rezervaci za poslednich 30 dni
    registrace_30denni_uspesnost_zmena_den = Column(Float)      # uspesnost rezervaci za poslednich 30 dni - zmena za den
    registrace_30denni_uspesnost_zmena_tyden = Column(Float)    # uspesnost rezervaci za poslednich 30 dni - zmena za tyden
    registrace_prumer_cekani = Column(Float)                    # prumerna doba cekani na rezervaci z poslednich 7 dni
    registrace_prumer_cekani_zmena_den = Column(Float)          # prumerna doba cekani na rezervaci z poslednich 7 dni - zmena za den
    registrace_prumer_cekani_zmena_tyden = Column(Float)        # prumerna doba cekani na rezervaci z poslednich 7 dni - zmena za tyden
    registrace_odhad_cekani = Column(Float)                     # odhadovana doba cekani na rezervaci
    registrace_odhad_cekani_zmena_den = Column(Float)           # odhadovana doba cekani na rezervaci - zmena za den
    registrace_odhad_cekani_zmena_tyden = Column(Float)         # odhadovana doba cekani na rezervaci - zmena za tyden
    registrace_fronta_prumer_cekani = Column(Float)             # prumerna doba ve fronte
    registrace_fronta_prumer_cekani_zmena_den = Column(Float)   # prumerna doba ve fronte - zmena za den
    registrace_fronta_prumer_cekani_zmena_tyden = Column(Float) # prumerna doba ve fronte - zmena za tyden
    ockovani_pocet_davek = Column(Integer)                      # pocet ockovanych davek
    ockovani_pocet_davek_zmena_den = Column(Integer)            # pocet ockovanych davek - zmena za den
    ockovani_pocet_davek_zmena_tyden = Column(Integer)          # pocet ockovanych davek - zmena za tyden
    ockovani_pocet_castecne = Column(Integer)                   # pocet ockovanych alespon castecne
    ockovani_pocet_castecne_zmena_den = Column(Integer)         # pocet ockovanych alespon castecne - zmena za den
    ockovani_pocet_castecne_zmena_tyden = Column(Integer)       # pocet ockovanych alespon castecne - zmena za tyden
    ockovani_pocet_plne = Column(Integer)                       # pocet ockovanych plne (vsechny davky)
    ockovani_pocet_plne_zmena_den = Column(Integer)             # pocet ockovanych plne (vsechny davky) - zmena za den
    ockovani_pocet_plne_zmena_tyden = Column(Integer)           # pocet ockovanych plne (vsechny davky) - zmena za tyden
    ockovani_odhad_cekani = Column(Float)                       # odhad casu potrebneho na naockovani lidi ve fronte a rezervaci
    ockovani_odhad_cekani_zmena_den = Column(Float)             # odhad casu potrebneho na naockovani lidi ve fronte a rezervaci - zmena za den
    ockovani_odhad_cekani_zmena_tyden = Column(Float)           # odhad casu potrebneho na naockovani lidi ve fronte a rezervaci - zmena za tyden
    vakciny_prijate_pocet = Column(Integer)                     # pocet prijatych vakcin
    vakciny_prijate_pocet_zmena_den = Column(Integer)           # pocet prijatych vakcin - zmena za den
    vakciny_prijate_pocet_zmena_tyden = Column(Integer)         # pocet prijatych vakcin - zmena za tyden
    vakciny_ockovane_pocet = Column(Integer)                    # pocet ockovanych vakcin
    vakciny_ockovane_pocet_zmena_den = Column(Integer)          # pocet ockovanych vakcin - zmena za den
    vakciny_ockovane_pocet_zmena_tyden = Column(Integer)        # pocet ockovanych vakcin - zmena za tyden
    vakciny_znicene_pocet = Column(Integer)                     # pocet znicenych vakcin
    vakciny_znicene_pocet_zmena_den = Column(Integer)           # pocet znicenych vakcin - zmena za den
    vakciny_znicene_pocet_zmena_tyden = Column(Integer)         # pocet znicenych vakcin - zmena za tyden
    vakciny_skladem_pocet = Column(Integer)                     # odhad vakcin skladem
    vakciny_skladem_pocet_zmena_den = Column(Integer)           # odhad vakcin skladem - zmena za den
    vakciny_skladem_pocet_zmena_tyden = Column(Integer)         # odhad vakcin skladem - zmena za tyden

    misto = relationship("OckovaciMisto", back_populates="metriky")

    def __repr__(self):
        return "<OckovaciMistoMetriky(id='%s', datum='%s')>" % (self.id, self.datum)


OckovaciMisto.metriky = relationship("OckovaciMistoMetriky", back_populates="misto")


class CrMetriky(db.Model):
    __tablename__ = 'cr_metriky'

    datum = Column(DateTime, primary_key=True)
    pocet_obyvatel_celkem = Column(Integer)
    pocet_obyvatel_dospeli = Column(Integer)
    rezervace_celkem = Column(Integer)                          # pocet vsech rezervaci (vsechny kalendare)
    rezervace_celkem_zmena_den = Column(Integer)                # pocet vsech rezervaci (vsechny kalendare) - zmena za den
    rezervace_celkem_zmena_tyden = Column(Integer)              # pocet vsech rezervaci (vsechny kalendare) - zmena za tyden
    rezervace_cekajici = Column(Integer)                        # pocet rezervaci cekajicich na ockovani (vsechny kalendare)
    rezervace_cekajici_zmena_den = Column(Integer)              # pocet rezervaci cekajicich na ockovani (vsechny kalendare) - zmena za den
    rezervace_cekajici_zmena_tyden = Column(Integer)            # pocet rezervaci cekajicich na ockovani (vsechny kalendare) - zmena za tyden
    rezervace_cekajici_1 = Column(Integer)                      # pocet rezervaci cekajicich na ockovani (kalendar pro 1. davky)
    rezervace_cekajici_1_zmena_den = Column(Integer)            # pocet rezervaci cekajicich na ockovani (kalendar pro 1. davky) - zmena za den
    rezervace_cekajici_1_zmena_tyden = Column(Integer)          # pocet rezervaci cekajicich na ockovani (kalendar pro 1. davky) - zmena za tyden
    rezervace_cekajici_2 = Column(Integer)                      # pocet rezervaci cekajicich na ockovani (kalendar pro 2. davky)
    rezervace_cekajici_2_zmena_den = Column(Integer)            # pocet rezervaci cekajicich na ockovani (kalendar pro 2. davky) - zmena za den
    rezervace_cekajici_2_zmena_tyden = Column(Integer)          # pocet rezervaci cekajicich na ockovani (kalendar pro 2. davky) - zmena za tyden
    rezervace_kapacita = Column(Integer)                        # kapacita na aktualni den (vsechny kalendare)
    rezervace_kapacita_zmena_den = Column(Integer)              # kapacita na aktualni den (vsechny kalendare) - zmena za den
    rezervace_kapacita_zmena_tyden = Column(Integer)            # kapacita na aktualni den (vsechny kalendare) - zmena za tyden
    rezervace_kapacita_1 = Column(Integer)                      # kapacita na aktualni den (kalendar pro 1. davky)
    rezervace_kapacita_1_zmena_den = Column(Integer)            # kapacita na aktualni den (kalendar pro 1. davky) - zmena za den
    rezervace_kapacita_1_zmena_tyden = Column(Integer)          # kapacita na aktualni den (kalendar pro 1. davky) - zmena za tyden
    rezervace_kapacita_2 = Column(Integer)                      # kapacita na aktualni den (kalendar pro 2. davky)
    rezervace_kapacita_2_zmena_den = Column(Integer)            # kapacita na aktualni den (kalendar pro 2. davky) - zmena za den
    rezervace_kapacita_2_zmena_tyden = Column(Integer)          # kapacita na aktualni den (kalendar pro 2. davky) - zmena za tyden
    registrace_celkem = Column(Integer)                         # pocet vsech registraci
    registrace_celkem_zmena_den = Column(Integer)               # pocet vsech registraci - zmena za den
    registrace_celkem_zmena_tyden = Column(Integer)             # pocet vsech registraci - zmena za tyden
    registrace_fronta = Column(Integer)                         # pocet registraci bez rezervace
    registrace_fronta_zmena_den = Column(Integer)               # pocet registraci bez rezervace - zmena za den
    registrace_fronta_zmena_tyden = Column(Integer)             # pocet registraci bez rezervace - zmena za tyden
    registrace_tydenni_uspesnost = Column(Float)                # uspesnost rezervaci za poslednich 7 dni
    registrace_tydenni_uspesnost_zmena_den = Column(Float)      # uspesnost rezervaci za poslednich 7 dni - zmena za den
    registrace_tydenni_uspesnost_zmena_tyden = Column(Float)    # uspesnost rezervaci za poslednich 7 dni - zmena za tyden
    registrace_14denni_uspesnost = Column(Float)                # uspesnost rezervaci za poslednich 14 dni
    registrace_14denni_uspesnost_zmena_den = Column(Float)      # uspesnost rezervaci za poslednich 14 dni - zmena za den
    registrace_14denni_uspesnost_zmena_tyden = Column(Float)    # uspesnost rezervaci za poslednich 14 dni - zmena za tyden
    registrace_30denni_uspesnost = Column(Float)                # uspesnost rezervaci za poslednich 30 dni
    registrace_30denni_uspesnost_zmena_den = Column(Float)      # uspesnost rezervaci za poslednich 30 dni - zmena za den
    registrace_30denni_uspesnost_zmena_tyden = Column(Float)    # uspesnost rezervaci za poslednich 30 dni - zmena za tyden
    registrace_prumer_cekani = Column(Float)                    # prumerna doba cekani na rezervaci z poslednich 7 dni
    registrace_prumer_cekani_zmena_den = Column(Float)          # prumerna doba cekani na rezervaci z poslednich 7 dni - zmena za den
    registrace_prumer_cekani_zmena_tyden = Column(Float)        # prumerna doba cekani na rezervaci z poslednich 7 dni - zmena za tyden
    registrace_fronta_prumer_cekani = Column(Float)             # prumerna doba ve fronte
    registrace_fronta_prumer_cekani_zmena_den = Column(Float)   # prumerna doba ve fronte - zmena za den
    registrace_fronta_prumer_cekani_zmena_tyden = Column(Float) # prumerna doba ve fronte - zmena za tyden
    ockovani_pocet_davek = Column(Integer)                      # pocet ockovanych davek
    ockovani_pocet_davek_zmena_den = Column(Integer)            # pocet ockovanych davek - zmena za den
    ockovani_pocet_davek_zmena_tyden = Column(Integer)          # pocet ockovanych davek - zmena za tyden
    ockovani_pocet_castecne = Column(Integer)                   # pocet ockovanych alespon castecne
    ockovani_pocet_castecne_zmena_den = Column(Integer)         # pocet ockovanych alespon castecne - zmena za den
    ockovani_pocet_castecne_zmena_tyden = Column(Integer)       # pocet ockovanych alespon castecne - zmena za tyden
    ockovani_pocet_plne = Column(Integer)                       # pocet ockovanych plne (vsechny davky)
    ockovani_pocet_plne_zmena_den = Column(Integer)             # pocet ockovanych plne (vsechny davky) - zmena za den
    ockovani_pocet_plne_zmena_tyden = Column(Integer)           # pocet ockovanych plne (vsechny davky) - zmena za tyden
    vakciny_prijate_pocet = Column(Integer)                     # pocet prijatych vakcin
    vakciny_prijate_pocet_zmena_den = Column(Integer)           # pocet prijatych vakcin - zmena za den
    vakciny_prijate_pocet_zmena_tyden = Column(Integer)         # pocet prijatych vakcin - zmena za tyden
    vakciny_ockovane_pocet = Column(Integer)                    # pocet ockovanych vakcin
    vakciny_ockovane_pocet_zmena_den = Column(Integer)          # pocet ockovanych vakcin - zmena za den
    vakciny_ockovane_pocet_zmena_tyden = Column(Integer)        # pocet ockovanych vakcin - zmena za tyden
    vakciny_znicene_pocet = Column(Integer)                     # pocet znicenych vakcin
    vakciny_znicene_pocet_zmena_den = Column(Integer)           # pocet znicenych vakcin - zmena za den
    vakciny_znicene_pocet_zmena_tyden = Column(Integer)         # pocet znicenych vakcin - zmena za tyden
    vakciny_skladem_pocet = Column(Integer)                     # odhad vakcin skladem
    vakciny_skladem_pocet_zmena_den = Column(Integer)           # odhad vakcin skladem - zmena za den
    vakciny_skladem_pocet_zmena_tyden = Column(Integer)         # odhad vakcin skladem - zmena za tyden

    def __repr__(self):
        return "<CrMetriky(datum='%s')>" % (self.datum)