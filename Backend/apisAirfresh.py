from datetime import datetime, timezone
import re
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session as SASession

from Backend.BdConexion import Session as SessionLocal, engine
from Backend.schemas.mediciones import MedicionOut
from Backend.schemas.promedios import PromedioOut

apiAirfresh = APIRouter(prefix="/ApiAirfresh", tags=["API Airfresh"])

@apiAirfresh.get("/mediciones/by-sensor-raw/{sensors_id}", response_model=List[MedicionOut])
async def mediciones_by_sensor_raw(sensors_id: int):
    db: SASession = SessionLocal()
    try:
        sql = text("""
            SELECT id, location_id, sensors_id, location, datetime, lat, lon, parameter, units, value
            FROM mediciones
            WHERE sensors_id = :sid
            ORDER BY datetime DESC
        """)
        rows = db.execute(sql, {"sid": sensors_id}).mappings().all()  # list[RowMapping]
        return [MedicionOut(**r) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando mediciones: {e}")
    finally:
        db.close()

@apiAirfresh.post("/promedios/compute-last5", response_model=PromedioOut)
def compute_promedio_last5(
    location_id: int = Query(..., description="ID de la ubicación"),
    parameter: str = Query(..., description="ej: pm10"),
    units: str = Query(..., description="ej: µg/m³"),
):
    try:
        saved = refresh_promedio_last5_sync(location_id, parameter, units)
        return saved  # PromedioOut castea automáticamente
    except ValueError as ve:
        # No había mediciones que cumplieran los filtros
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error guardando promedio: {e}")


@apiAirfresh.get("/mediciones/by-location-raw/{location_id}", response_model=List[MedicionOut])
async def mediciones_by_location_raw(
    location_id: int,
    parameter: Optional[str] = Query(None),
    units: Optional[str] = Query(None),
    limit: int = Query(500, ge=1, le=10000),
):
    db: SASession = SessionLocal()
    try:
        where = ["location_id = :loc"]
        params = {"loc": location_id}

        if parameter:
            where.append("parameter = :parameter")
            params["parameter"] = parameter
        if units:
            where.append("units = :units")
            params["units"] = units

        sql = text(f"""
            SELECT id, location_id, sensors_id, location, datetime, lat, lon, parameter, units, value
            FROM mediciones
            WHERE {' AND '.join(where)}
            ORDER BY datetime DESC
            LIMIT :limit
        """)
        params["limit"] = limit

        rows = db.execute(sql, params).mappings().all()
        return [MedicionOut(**r) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando mediciones: {e}")
    finally:
        db.close()

@apiAirfresh.get("/mediciones/by-location-raw/{location_id}", response_model=List[MedicionOut])
async def mediciones_by_location_raw(location_id: int):
    db: SASession = SessionLocal()
    try:
        sql = text("""
            SELECT id, location_id, sensors_id, location, datetime, lat, lon, parameter, units, value
            FROM mediciones
            WHERE location_id = :loc
            ORDER BY datetime DESC
        """)
        rows = db.execute(sql, {"loc": location_id}).mappings().all()
        return [MedicionOut(**r) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando mediciones: {e}")
    finally:
        db.close()

@apiAirfresh.get("/mediciones/by-location-raw2/{location_id}", response_model=List[MedicionOut])
def mediciones_by_location_raw(
    location_id: int,
    parameter: Optional[str] = Query(None, description="p. ej., pm10"),
    units: Optional[str] = Query(None, description="p. ej., µg/m³, ug/m3"),
    limit: int = Query(500, ge=1, le=10000),
):
    # --- Normalización en Python para 'units' ---
    def norm_units_py(u: str) -> str:
        # micro a 'u'
        u = u.replace("µ", "u").replace("μ", "u")
        u = u.lower()
        # quitar todo lo que no sea a-z0-9
        return re.sub(r"[^a-z0-9]", "", u)  # "µg/m³" -> "ugm3"
    
    where = ["location_id = :loc"]
    params = {"loc": location_id, "limit": limit}

    if parameter:
        where.append("LOWER(parameter) = LOWER(:parameter)")
        params["parameter"] = parameter

    units_norm_clause = ""
    if units:
        params["units_norm"] = norm_units_py(units)
        # Normalización equivalente del lado SQL:
        #  - micro a 'u' (replace)
        #  - lower
        #  - quitar no alfanuméricos (regexp_replace)
        units_norm_clause = """
            AND regexp_replace(
                    replace(replace(lower(units), 'µ', 'u'), 'μ', 'u'),
                    '[^a-z0-9]', '', 'g'
                ) = :units_norm
        """

    sql = text(f"""
        SELECT id, location_id, sensors_id, location, datetime, lat, lon, parameter, units, value
        FROM mediciones
        WHERE {' AND '.join(where)} {units_norm_clause}
        ORDER BY datetime DESC
        LIMIT :limit
    """)

    db: SASession = SessionLocal()
    try:
        rows = db.execute(sql, params).mappings().all()
        return [MedicionOut(**r) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando mediciones: {e}")
    finally:
        db.close()


def _norm_units_py(u: str) -> str:
    # "µg/m³" -> "ugm3"
    u = u.replace("µ", "u").replace("μ", "u").lower()
    return re.sub(r"[^a-z0-9]", "", u)


def refresh_promedio_last5_sync(location_id: int, parameter: str, units: str) -> dict:
    """
    Calcula el promedio de las últimas 5 mediciones para (location_id, parameter, units)
    y lo guarda/actualiza en la tabla 'promedios'. Devuelve el registro guardado.
    """
    with SessionLocal() as db:
        # 1) Tomar las últimas 5 mediciones (por datetime DESC) y agregarlas
        q = text("""
            WITH last5 AS (
                SELECT value, datetime
                FROM mediciones
                WHERE location_id = :location_id
                  AND LOWER(parameter) = LOWER(:parameter)
                  AND units = :units
                ORDER BY datetime DESC
                LIMIT 5
            )
            SELECT
                AVG(value)::float8        AS avg_value,
                COUNT(*)                  AS n,
                MIN(datetime)             AS from_ts,
                MAX(datetime)             AS to_ts
            FROM last5;
        """)
        agg = db.execute(q, {
            "location_id": location_id,
            "parameter": parameter,
            "units": units
        }).mappings().first()

        # Sin filas → no hay nada que guardar
        if not agg or not agg["n"]:
            raise ValueError("No hay mediciones para los filtros indicados.")

        avg_value = float(agg["avg_value"])
        n = int(agg["n"])
        from_ts = agg["from_ts"]
        to_ts = agg["to_ts"]
        computed_at = datetime.now(timezone.utc)

        # 2) UPSERT en promedios (se requiere UNIQUE en (location_id, parameter, units))
        upsert = text("""
            INSERT INTO promedios (location_id, parameter, units, avg_value, n, from_ts, to_ts, computed_at)
            VALUES (:location_id, :parameter, :units, :avg_value, :n, :from_ts, :to_ts, :computed_at)
            ON CONFLICT (location_id, parameter, units)
            DO UPDATE SET
                avg_value   = EXCLUDED.avg_value,
                n           = EXCLUDED.n,
                from_ts     = EXCLUDED.from_ts,
                to_ts       = EXCLUDED.to_ts,
                computed_at = EXCLUDED.computed_at
            RETURNING location_id, parameter, units, avg_value, n, from_ts, to_ts, computed_at;
        """)
        row = db.execute(upsert, {
            "location_id": location_id,
            "parameter": parameter,
            "units": units,
            "avg_value": avg_value,
            "n": n,
            "from_ts": from_ts,
            "to_ts": to_ts,
            "computed_at": computed_at
        }).mappings().first()

        db.commit()
        return dict(row)