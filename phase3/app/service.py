from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Iterable, List, Optional, Tuple

import httpx

from .settings import (
    SENSEMAP_BASE_URL,
    HTTP_TIMEOUT,
    SENSEMAP_LOOKBACK_HOURS,
)

logger = logging.getLogger(__name__)


def average(values: Iterable[float]) -> Optional[float]:
    """Return arithmetic mean or None for empty input."""
    vals = list(values)
    if not vals:
        return None
    return sum(vals) / len(vals)


def _parse_iso(ts: str) -> Optional[datetime]:
    """Parse ISO-8601 timestamp; tolerate trailing 'Z' by normalizing to +00:00."""
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except Exception:
        return None


def _extract_last_measurement(sensor: dict) -> Optional[Tuple[float, datetime]]:
    """
    Try multiple shapes that openSenseMap uses for 'last measurement':

    1) sensor["lastMeasurement"] is a dict:
       {"value": "...", "createdAt": "..."}
    2) sensor["lastMeasurement"] is an ISO string timestamp,
       with value stored in sensor["lastMeasurementValue"].
    3) Alternative keys:
       sensor["lastMeasurementAt"] (ISO), sensor["lastMeasurementValue"] (number/string)

    Returns:
        (value_float, timestamp) or None if not parseable.
    """
    lm = sensor.get("lastMeasurement")

    # Case 1: object/dict
    if isinstance(lm, dict):
        val = lm.get("value")
        ts = _parse_iso(lm.get("createdAt", ""))
        if val is not None and ts is not None:
            try:
                return float(val), ts
            except (TypeError, ValueError):
                pass

    # Case 2: lastMeasurement is a string timestamp, value in lastMeasurementValue
    if isinstance(lm, str):
        ts = _parse_iso(lm)
        val = sensor.get("lastMeasurementValue")
        if ts is not None and val is not None:
            try:
                return float(val), ts
            except (TypeError, ValueError):
                pass

    # Case 3: alternative key names
    ts2 = _parse_iso(sensor.get("lastMeasurementAt", ""))
    val2 = sensor.get("lastMeasurementValue")
    if ts2 is not None and val2 is not None:
        try:
            return float(val2), ts2
        except (TypeError, ValueError):
            pass

    return None


class SenseMapClient:
    """
    Minimal client to fetch temperature measurements from openSenseMap.

    Strategy:
      1) Try /boxes?full=true to get sensors with lastMeasurement included.
      2) If nothing found, try /boxes/data with phenomenon & from-date as a fallback.
    """

    def __init__(self, base_url: str = SENSEMAP_BASE_URL, timeout: float = HTTP_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def fetch_temperatures(self, hours: Optional[int] = None) -> List[float]:
        """
        Fetch temperature readings not older than `hours` (default from settings),
        and return them as floats (°C).
        """
        lookback = hours if hours is not None else SENSEMAP_LOOKBACK_HOURS
        since = datetime.now(timezone.utc) - timedelta(hours=lookback)

        temps: List[float] = []

        # ---- Attempt 1: /boxes?full=true ----
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                boxes_url = f"{self.base_url}/boxes"
                params = {
                    "full": "true",   # include sensors with lastMeasurement
                    "format": "json",
                }
                r1 = await client.get(boxes_url, params=params)
                r1.raise_for_status()
                data = r1.json()
        except Exception as e:
            logger.warning("GET /boxes failed: %s", e)
            data = []

        if isinstance(data, list):
            found_boxes = len(data)
            found_sensors = 0
            for box in data:
                for sensor in box.get("sensors", []):
                    found_sensors += 1
                    title = str(sensor.get("title", "")).lower()
                    phen = str(sensor.get("phenomenon", "")).lower()
                    is_temp = any(
                        key in title or key in phen
                        for key in ("temp", "temperatur", "temperature", "lufttemperatur", "air temperature")
                    )
                    if not is_temp:
                        continue

                    parsed = _extract_last_measurement(sensor)
                    if not parsed:
                        continue

                    val, ts = parsed
                    if ts >= since:
                        temps.append(val)

            logger.info(
                "[/boxes] boxes=%d, sensors=%d, temps_in_window=%d (last %d h)",
                found_boxes, found_sensors, len(temps), lookback,
            )

        if temps:
            return temps

        # ---- Attempt 2: fallback to /boxes/data ----
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                data_url = f"{self.base_url}/boxes/data"
                params2 = {
                    "phenomenon": "temperature",
                    "from-date": since.isoformat(),
                    "format": "json",
                }
                r2 = await client.get(data_url, params=params2)
                r2.raise_for_status()
                data2 = r2.json()
        except Exception as e:
            logger.warning("GET /boxes/data fallback failed: %s", e)
            data2 = []

        if isinstance(data2, list):
            taken = 0
            for row in data2:
                val = row.get("value")
                ts = _parse_iso(row.get("createdAt", ""))
                if val is None or ts is None:
                    continue
                if ts >= since:
                    try:
                        temps.append(float(val))
                        taken += 1
                    except (TypeError, ValueError):
                        continue
            logger.info("[/boxes/data] measurements_in_window=%d (last %d h)", taken, lookback)

        return temps
