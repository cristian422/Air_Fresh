# jobs_promedios.py
from sqlalchemy import text
from BdConexion import Session as SessionLocal  # tu SessionLocal síncrona

DDL_PROMEDIOS = """
CREATE TABLE IF NOT EXISTS promedios (
  location_id   INTEGER NOT NULL,
  parameter     TEXT    NOT NULL,
  units         TEXT    NOT NULL,
  avg_value     NUMERIC NOT NULL,
  n             INTEGER NOT NULL,
  from_ts       TIMESTAMPTZ NOT NULL,
  to_ts         TIMESTAMPTZ NOT NULL,
  computed_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (location_id, parameter, units)
);
"""

CREATE_INDEX_MEDICIONES = """
CREATE INDEX IF NOT EXISTS idx_med_ult5
ON mediciones (location_id, parameter, units, datetime DESC, id DESC);
"""

UPSERT_PROMEDIOS = """
WITH ranked AS (
  SELECT
    m.*,
    ROW_NUMBER() OVER (
      PARTITION BY m.location_id, m.parameter, m.units
      ORDER BY m.datetime DESC, m.id DESC
    ) AS rn
  FROM mediciones m
),
last5 AS (
  SELECT
    location_id,
    parameter,
    units,
    AVG(value)    AS avg_value,
    COUNT(*)      AS n,
    MIN(datetime) AS from_ts,
    MAX(datetime) AS to_ts
  FROM ranked
  WHERE rn <= 5
  GROUP BY location_id, parameter, units
)
INSERT INTO promedios (location_id, parameter, units, avg_value, n, from_ts, to_ts, computed_at)
SELECT location_id, parameter, units, avg_value, n, from_ts, to_ts, now()
FROM last5
ON CONFLICT (location_id, parameter, units)
DO UPDATE SET
  avg_value   = EXCLUDED.avg_value,
  n           = EXCLUDED.n,
  from_ts     = EXCLUDED.from_ts,
  to_ts       = EXCLUDED.to_ts,
  computed_at = EXCLUDED.computed_at;
"""

def refresh_promedios_sync() -> None:
    """
    Calcula el promedio de las últimas 5 mediciones por (location_id, parameter, units)
    y hace UPSERT en la tabla 'promedios'.
    """
    db = SessionLocal()
    try:
        db.execute(text(DDL_PROMEDIOS))
        db.execute(text(CREATE_INDEX_MEDICIONES))
        db.execute(text(UPSERT_PROMEDIOS))
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
