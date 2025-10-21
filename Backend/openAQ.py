# openaq.py
from fastapi import APIRouter, HTTPException, Request
from dotenv import load_dotenv
import os
import httpx
from models.mediciones import Medicion  # ✅ este es el ORM, no el schema
from Backend.BdConexion import Session  # ✅ cliente correcto
from datetime import datetime

airRouter = APIRouter(prefix="/air", tags=["Air Quality"])

load_dotenv()
OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY")
BASE = "https://api.openaq.org/v3"


async def get_openaq_Bylocation(location_id: int, params: dict | None = None):
    url = f"{BASE}/locations/{location_id}"
    headers = {"X-API-Key": OPENAQ_API_KEY}

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, headers=headers, params=params or {})
    resp.raise_for_status()

    data = resp.json()
    result = data["results"][0]

    first_sensor = result.get("sensors", [{}])[0]
    parameter_info = first_sensor.get("parameter", {})

    return {
        "location_id": result.get("id"),
        "sensors_id": first_sensor.get("id"),      # tu columna se llama sensors_id
        "location": result.get("name"),
        "datetime": result.get("datetimeLast", {}).get("utc"),
        "lat": result.get("coordinates", {}).get("latitude"),
        "lon": result.get("coordinates", {}).get("longitude"),
        "parameter": parameter_info.get("name"),
        "units": parameter_info.get("units"),
        "value": None,  # /locations no trae value; eso viene de /measurements
    }

def parse_utc(dt_str: str | None):
    if not dt_str:
        return None
    return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))


def save_location_data(data: dict):
    session = Session()
    try:
        medicion = Medicion(
            location_id = data.get("location_id"),
            sensors_id  = data.get("sensor_id") or data.get("sensors_id"),  # ← mapea aquí
            location    = data.get("location"),
            datetime    = parse_utc(data.get("datetime")),
            lat         = data.get("lat"),
            lon         = data.get("lon"),
            parameter   = data.get("parameter"),
            units       = data.get("units"),
            value       = data.get("value"),
        )
        session.add(medicion)
        session.commit()
        session.refresh(medicion)
        print("Saved:", medicion.id)
        return medicion.id
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()


@airRouter.get("/locations/{location_id}")
async def MetureAir_BY_ID(location_id: int, request: Request):
    filtered = await get_openaq_Bylocation(location_id, request=request)
    save_location_data(filtered)
    return {
        "message": "✅ Location data saved to database",
        "data": filtered
    }
