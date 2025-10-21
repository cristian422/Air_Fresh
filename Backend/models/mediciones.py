from sqlalchemy import Column, Integer, String
from Backend.BdConexion import Base   # ✅ importa tu Base de bd.py

from sqlalchemy import Column, Integer, String, Numeric, TIMESTAMP



class Medicion(Base):
    __tablename__ = "mediciones"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, index=True)
    sensors_id = Column(Integer, index=True)
    location = Column(String, index=True)
    datetime = Column(TIMESTAMP, index=True)
    lat = Column(Numeric)
    lon = Column(Numeric)
    parameter = Column(String)
    units = Column(String)
    value = Column(Numeric)
