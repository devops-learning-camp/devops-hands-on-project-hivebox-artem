import os
from typing import Final

APP_VERSION: Final[str] = os.getenv("APP_VERSION", "v0.0.1")
SENSEMAP_BASE_URL: Final[str] = os.getenv("SENSEMAP_BASE_URL", "https://api.opensensemap.org")
HTTP_TIMEOUT: Final[float] = float(os.getenv("HTTP_TIMEOUT", "10.0"))

# NEW: lookback window in hours (default 1)
SENSEMAP_LOOKBACK_HOURS: Final[int] = int(os.getenv("SENSEMAP_LOOKBACK_HOURS", "1"))
