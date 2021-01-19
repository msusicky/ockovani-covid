from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, Unicode, DateTime

db = SQLAlchemy()


class OckovaciMisto(db.Model):
    misto_id = Column(Integer, primary_key=True)
    nazev = Column(Unicode)
    service_id = Column(Integer)
    operation_id = Column(Integer)
    place_id = Column(Integer)
    mesto = Column(Unicode)


class OckovaciMistoKapacita(db.Model):
    misto_id = Column(Integer, primary_key=True)
    nazev = Column(Unicode)
    service_id = Column(Integer)
    operation_id = Column(Integer)
    place_id = Column(Integer)
    mesto = Column(Unicode)
    pocet_mist = Column(Integer)


class VolnaMistaQuery(db.Model):
    query = Column(Unicode, primary_key=True)


class OckovaciKapacity(db.Model):
    mesto = Column(Unicode)
    nazev = Column(Unicode)
    datum = Column(DateTime, primary_key=True)
    pocet_mist = Column(Integer)
    misto_id = Column(Integer, primary_key=True)

    def __repr__(self):
        return f"{self.mesto} - {self.nazev}:{self.misto_id} - {self.datum}: {self.pocet_mist}"


class Kapacita(db.Model):
    misto_id = Column(Integer, primary_key=True)
    datum = Column(DateTime, primary_key=True)
    raw_data = Column(Unicode)
    pocet_mist = Column(Integer)
    datum_ziskani = Column(DateTime, primary_key=True, default=datetime.now)
    import_id = Column(Integer)


class Dny(db.Model):
    den_id = Column(Integer, primary_key=True)
    datum = Column(DateTime)


class ImportLog(db.Model):
    import_id = Column(Integer, primary_key=True)
    spusteni = Column(DateTime)

