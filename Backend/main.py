#impor fastapi
from fastapi import FastAPI, APIRouter
#impor routers
#from appi import traficoRouter
from Backend.apScheduler.apScheduler import start_jobs, stop_jobs
from Backend.BdConexion import engine, Base
from Backend.models.mediciones import Medicion
# que es contextlib?
# utilidades para context managers async
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # === Startup ===
    # Crear tablas si no existen
    print("🔧 Inicializando base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos lista!")
    
    start_jobs()                 # enciende APScheduler
    try:
        yield                    # la app queda corriendo
    finally:
        # === Shutdown ===
        stop_jobs()              # apaga APScheduler limpiamente

app = FastAPI(title="FreshAir API",
    description="API para obtener datos de calidad del aire y tráfico en tiempo real",
    version="1.0.0",
    lifespan=lifespan,
)

#app.include_router(traficoRouter, prefix="/trafico", tags=["Trafico"])
#incluimos el router de calidad del aire
from Backend.openAQ import airRouter
from Backend.BDquery.BdConsultas import BdConsultas
from Backend.apisAirfresh import apiAirfresh
app.include_router(apiAirfresh)
app.include_router(BdConsultas)
app.include_router(airRouter)


