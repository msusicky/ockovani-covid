from datetime import datetime
from sqlalchemy import Column, Integer, Unicode, DateTime, Boolean, Float, Date, JSON, Sequence, ForeignKey
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
        return "<Okres(nazev='%s')>" % (self.nazev)


class OckovaciMisto(db.Model):
    __tablename__ = 'ockovaci_mista'

    id = Column(Unicode, primary_key=True)
    nazev = Column(Unicode)
    okres_id = Column(Unicode, ForeignKey('okresy.id'))
    status = Column(Boolean)
    adresa = Column(Unicode)
    latitude = Column(Float)
    longitude = Column(Float)
    minimalni_kapacita = Column(Integer)
    bezbarierovy_pristup = Column(Boolean)
    service_id = Column(Integer)
    operation_id = Column(Integer)
    odkaz = Column(Unicode)

    okres = relationship("Okres", back_populates="ockovaci_mista")

    def __repr__(self):
        return "<OckovaciMisto(nazev='%s', service_id=%s, operation_id=%s)>" % (self.nazev, self.service_id, self.operation_id)


class Import(db.Model):
    __tablename__ = 'importy'

    id = Column(Integer, Sequence('import_id_seq'), primary_key=True)
    start = Column(DateTime, default=datetime.now())
    status = Column(Unicode)

    def __repr__(self):
        return "<Import(id=%s, start='%s', status='%s')>" % (self.id, self.start, self.status)


class VolnaMista(db.Model):
    __tablename__ = 'volna_mista'

    id = Column(Integer, Sequence('volna_mista_id_seq'), primary_key=True)
    import_id = Column(Integer, ForeignKey('importy.id'))
    cas_ziskani = Column(DateTime, default=datetime.now())
    misto_id = Column(Unicode, ForeignKey('ockovaci_mista.id'))
    datum = Column(Date)
    cas = Column(Unicode)
    start = Column(DateTime)
    volna_mista = Column(Integer)
    place_id = Column(Integer)
    user_service_id = Column(Integer)

    import_ = relationship('Import', 'volna_mista')
    misto = relationship('OckovaciMisto', 'volna_mista')

    def __repr__(self):
        return "<VolnaMista(misto='%s', cas='%s', volna_mista=%s)>" % (self.misto.nazev, self.start, self.volna_mista)


class VolnaMistaRaw(db.Model):
    __tablename__ = 'volna_mista_raw'

    id = Column(Integer, Sequence('volna_mista_raw_id_seq'), primary_key=True)
    import_id = Column(Integer, ForeignKey('importy.id'))
    cas_ziskani = Column(DateTime, default=datetime.now())
    misto_id = Column(Unicode, ForeignKey('ockovaci_mista.id'))
    datum = Column(Date)
    data = Column(JSON)

    import_ = relationship('Import', 'volna_mista')
    misto = relationship('OckovaciMisto', 'volna_mista')

    def __repr__(self):
        return "<VolnaMistaRaw(misto='%s', datum='%s')>" % (self.misto.nazev, self.datum)
