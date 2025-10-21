# schemas/promedios.py (Pydantic v2)
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class PromedioOut(BaseModel):
    location_id: int
    parameter: str
    units: str
    avg_value: float
    n: int
    from_ts: datetime
    to_ts: datetime
    computed_at: datetime

    model_config = ConfigDict(from_attributes=True)
