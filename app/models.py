from datetime import datetime
from sqlalchemy import Column, Integer, Unicode, DateTime, Boolean, Float, Date, JSON, Sequence, ForeignKey
from sqlalchemy.orm import relationship

from app import db


class Kraj(db.Model):
    __tablename__ = 'kraje'

    id = Column(Unicode, primary_key=True)
    nazev = Column(Unicode)


class KrajMetriky(db.Model):
    __tablename__ = 'kraje_metriky'

    id = Column(Unicode, ForeignKey('kraje.id'), primary_key=True)
    datum = Column(DateTime, primary_key=True)
    typ_metriky = Column(Unicode, primary_key=True)
    hodnota_int = Column(Integer)
    hodnota_str = Column(Unicode)

    kraj = relationship("Kraj", back_populates="metriky")

    def __repr__(self):
        return "<KrajMetriky(id='%s', typ_metriky='%s', hodnota_int=%s, hodnota_str='%s')>" % (
            self.id, self.typ_metriky, self.hodnota_int, self.hodnota_str)


Kraj.metriky = relationship("KrajMetriky", back_populates="kraj")


class Okres(db.Model):
    __tablename__ = 'okresy'

    id = Column(Unicode, primary_key=True)
    nazev = Column(Unicode)
    kraj_id = Column(Unicode, ForeignKey('kraje.id'))

    kraj = relationship("Kraj", back_populates="okresy")

    def __repr__(self):
        return "<Okres(nazev='%s')>" % self.nazev


Kraj.okresy = relationship("Okres", back_populates="kraj")


class OkresMetriky(db.Model):
    __tablename__ = 'okresy_metriky'

    id = Column(Unicode, ForeignKey('okresy.id'), primary_key=True)
    datum = Column(DateTime, primary_key=True)
    typ_metriky = Column(Unicode, primary_key=True)
    hodnota_int = Column(Integer)
    hodnota_str = Column(Unicode)

    okres = relationship("Okres", back_populates="metriky")

    def __repr__(self):
        return "<OkresMetriky(id='%s', typ_metriky='%s', hodnota_int=%s, hodnota_str='%s')>" % (
            self.id, self.typ_metriky, self.hodnota_int, self.hodnota_str)


Okres.metriky = relationship("OkresMetriky", back_populates="okres")


class Populace(db.Model):
    __tablename__ = 'populace'

    orp_kod = Column(Unicode, primary_key=True)
    pocet = Column(Integer, primary_key=True)
    vek = Column(Integer, primary_key=True)

    def __repr__(self):
        return "<Populace(orp_kod='%s', pocet=%s, vek=%s)>" % (
            self.orp_kod, self.pocet, self.vek)


class OckovaciMisto(db.Model):
    __tablename__ = 'ockovaci_mista'

    id = Column(Unicode, primary_key=True)
    nazev = Column(Unicode)
    okres_id = Column(Unicode, ForeignKey('okresy.id'))
    status = Column(Boolean)
    adresa = Column(Unicode)
    latitude = Column(Float)
    longitude = Column(Float)
    nrpzs_kod = Column(Unicode)
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


class OckovaciMistoMetriky(db.Model):
    __tablename__ = 'ockovaci_mista_metriky'

    id = Column(Unicode, ForeignKey('ockovaci_mista.id'), primary_key=True)
    datum = Column(DateTime, primary_key=True)
    rezervace_celkem = Column(Integer)                      # pocet vsech rezervaci (vsechny kalendare)
    rezervace_celkem_zmena_den = Column(Integer)            # pocet vsech rezervaci (vsechny kalendare) - zmena za den
    rezervace_cekajici = Column(Integer)                    # pocet rezervaci cekajicich na ockovani (vsechny kalendare)
    rezervace_cekajici_zmena_den = Column(Integer)          # pocet rezervaci cekajicich na ockovani (vsechny kalendare) - zmena za den
    registrace_celkem = Column(Integer)                     # pocet vsech registraci
    registrace_celkem_zmena_den = Column(Integer)           # pocet vsech registraci - zmena za den
    registrace_fronta = Column(Integer)                     # pocet registraci bez rezervace
    registrace_fronta_zmena_den = Column(Integer)           # pocet registraci bez rezervace - zmena za den
    registrace_tydenni_uspesnost = Column(Float)            # uspesnost rezervaci za poslednich 7 dni
    registrace_tydenni_uspesnost_zmena_den = Column(Float)  # uspesnost rezervaci za poslednich 7 dni - zmena za den
    registrace_prumer_cekani = Column(Float)                # prumerna doba cekani na rezervaci z poslednich 7 dni
    registrace_prumer_cekani_zmena_den = Column(Float)      # prumerna doba cekani na rezervaci z poslednich 7 dni - zmena za den
    registrace_odhad_cekani = Column(Float)                 # odhadovana doba cekani na rezervaci
    registrace_odhad_cekani_zmena_den = Column(Float)       # odhadovana doba cekani na rezervaci - zmena za den
    ockovani_pocet = Column(Integer)                        # pocet ockovanych
    ockovani_pocet_zmena_den = Column(Integer)              # pocet ockovanych - zmena za den
    ockovani_pocet_zmena_tyden = Column(Integer)            # pocet ockovanych - zmena za tyden
    ockovani_odhad_cekani = Column(Float)                   # odhad casu potrebneho na naockovani lidi ve fronte a rezervaci
    ockovani_odhad_cekani_zmena_den = Column(Float)         # odhad casu potrebneho na naockovani lidi ve fronte a rezervaci - zmena za den
    vakciny_prijate_pocet = Column(Integer)                 # pocet prijatych vakcin
    vakciny_prijate_pocet_zmena_den = Column(Integer)       # pocet prijatych vakcin - zmena za den
    vakciny_prijate_pocet_zmena_tyden = Column(Integer)     # pocet prijatych vakcin - zmena za tyden
    vakciny_vydane_pocet = Column(Integer)                  # pocet vydanych vakcin
    vakciny_vydane_pocet_zmena_den = Column(Integer)        # pocet vydanych vakcin - zmena za den
    vakciny_vydane_pocet_zmena_tyden = Column(Integer)      # pocet vydanych vakcin - zmena za tyden
    vakciny_ockovane_pocet = Column(Integer)                # pocet ockovanych vakcin
    vakciny_ockovane_pocet_zmena_den = Column(Integer)      # pocet ockovanych vakcin - zmena za den
    vakciny_ockovane_pocet_zmena_tyden = Column(Integer)    # pocet ockovanych vakcin - zmena za tyden
    vakciny_znicene_pocet = Column(Integer)                 # pocet znicenych vakcin
    vakciny_znicene_pocet_zmena_den = Column(Integer)       # pocet znicenych vakcin - zmena za den
    vakciny_znicene_pocet_zmena_tyden = Column(Integer)     # pocet znicenych vakcin - zmena za tyden

    misto = relationship("OckovaciMisto", back_populates="metriky")

    def __repr__(self):
        return "<OckovaciMistoMetriky(id='%s', datum='%s')>" % (self.id, self.datum)


OckovaciMisto.metriky = relationship("OckovaciMistoMetriky", back_populates="misto")


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
    ockovaci_misto_id = Column(Unicode, ForeignKey('ockovaci_mista.id'), primary_key=True)
    cilove_ockovaci_misto_id = Column(Unicode, primary_key=True)
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
    kraj_nuts_kod = Column(Unicode)
    kraj_nazev = Column(Unicode)
    zarizeni_kod = Column(Unicode, primary_key=True)
    zarizeni_nazev = Column(Unicode)
    poradi_davky = Column(Integer, primary_key=True)
    vekova_skupina = Column(Unicode, primary_key=True)
    pocet = Column(Integer)

    def __repr__(self):
        return "<OckovaniLide(zarizeni_nazev='%s', vakcina='%s', datum='%s', poradi_davky=%s, vekova_skupina='%s', pocet=%s)>" % (
            self.zarizeni_nazev, self.vakcina, self.datum, self.poradi_davky, self.vekova_skupina,
            self.pocet)


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
    pocet_zmena = Column(Integer)

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
    volna_kapacita_zmena = Column(Integer)
    maximalni_kapacita_zmena = Column(Integer)

    import_ = relationship('Import', back_populates='ockovani_rezervace')
    misto = relationship('OckovaciMisto', back_populates='ockovani_rezervace')

    def __repr__(self):
        return "<OckovaniRezervace(ockovaci_misto_id='%s', datum='%s', volna_kapacita='%s', kalendar_ockovani='%s')>" % (
            self.ockovaci_misto_id, self.datum, self.volna_kapacita, self.kalendar_ockovani)


Import.ockovani_rezervace = relationship("OckovaniRezervace", back_populates="import_", cascade="delete")
OckovaciMisto.ockovani_rezervace = relationship("OckovaniRezervace", back_populates="misto")
