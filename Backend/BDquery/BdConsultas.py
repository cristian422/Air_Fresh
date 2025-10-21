from fastapi import APIRouter
from sqlalchemy import text
from Backend.BdConexion import Session  # <-- tu sesión síncrona

BdConsultas = APIRouter(prefix="/consulta", tags=["consultas bd"])

def query_mediciones(location_id: int, limit: int = 50):
    sql = text("""
        SELECT id, location_id, sensors_id, location, datetime, lat, lon, parameter, units, value
        FROM mediciones
        WHERE location_id = :loc
        ORDER BY datetime DESC
        LIMIT :lim
    """)
    with Session() as s:
        result = s.execute(sql, {"loc": location_id, "lim": limit})
        rows = result.mappings().all()
        return [dict(r) for r in rows]

@BdConsultas.get("/mediciones/by-location")
def mediciones_by_location(location_id: int, limit: int = 50):
    data = query_mediciones(location_id, limit)
    return {"data": data}#ya esta devolviendo un diccionario o un json {"data": [...]}{clave: valor}

