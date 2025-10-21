# apScheduler/apScheduler.py
import asyncio
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from Backend.openAQ import get_openaq_Bylocation, save_location_data
from Backend.apScheduler.jobs_promedios import refresh_promedios_sync

MONITORED_IDS = {2163023}
scheduler: AsyncIOScheduler | None = None  # referencia global

async def poll_one(location_id: int):
    try:
        data = await get_openaq_Bylocation(location_id, params={})
        save_location_data(data)
        print(f"[JOB] saved {location_id} @{data.get('datetime')}", flush=True)
    except Exception as e:
        print(f"[JOB ERR] {location_id}: {e}", flush=True)

async def poll_all(ids):
    await asyncio.gather(*(poll_one(i) for i in ids))

async def refresh_promedios_job():
    try:
        # correr función SINCRONA en un hilo, por cada location
        await asyncio.gather(
            *(asyncio.to_thread(refresh_promedios_sync, loc_id) for loc_id in MONITORED_IDS)
        )
        print(f"[JOB] promedios actualizados para {sorted(MONITORED_IDS)}", flush=True)
    except Exception as e:
        print(f"[JOB ERR] refresh_promedios_job: {e}", flush=True)

def start_jobs():
    global scheduler
    loop = asyncio.get_running_loop()                 # ← ahora sí hay loop (lifespan)
    scheduler = AsyncIOScheduler(timezone="UTC", event_loop=loop)

    # Agenda la corutina DIRECTAMENTE (sin create_task ni lambda)
    scheduler.add_job(
        poll_all,                                     # ← función async
        args=[MONITORED_IDS],
        trigger=IntervalTrigger(minutes=5),
        id="poll_openaq_2min",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=60,
        next_run_time=datetime.now(timezone.utc),     # corre ya
    )
    scheduler.add_job(
        refresh_promedios_job,
        trigger=IntervalTrigger(minutes=60),
        id="refresh_promedios_15min",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=60,
        next_run_time=datetime.now(timezone.utc).replace(second=0, microsecond=0) + 
                       (datetime.now(timezone.utc) - datetime.now(timezone.utc))  # opcional: arranque inmediato
    )
    print("[SCHED] started", flush=True)
    scheduler.start()

def stop_jobs():
    if scheduler:
        print("[SCHED] stopping", flush=True)
        scheduler.shutdown(wait=False)
