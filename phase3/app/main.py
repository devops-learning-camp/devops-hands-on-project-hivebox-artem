from __future__ import annotations
from fastapi import FastAPI, HTTPException

from .settings import APP_VERSION, SENSEMAP_LOOKBACK_HOURS
from .service import SenseMapClient, average

app = FastAPI(title="Phase-03 API", version=APP_VERSION)

@app.get("/version")
async def get_version():
    """Returns the deployed app version."""
    return {"version": APP_VERSION}

@app.get("/temperature")
async def get_current_average_temperature():
    client = SenseMapClient()
    temps = await client.fetch_temperatures()  # <= новый метод
    avg = average(temps)
    if avg is None:
        raise HTTPException(
            status_code=404,
            detail=f"No temperature data in the last {SENSEMAP_LOOKBACK_HOURS} hour(s)",
        )
    return {"average_temperature": round(avg, 2), "unit": "°C", "lookback_hours": SENSEMAP_LOOKBACK_HOURS}

