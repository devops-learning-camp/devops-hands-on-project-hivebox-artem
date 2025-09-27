# Phase 03 – FastAPI Service

**Endpoints**

- `GET /version` → returns current app version (from `APP_VERSION` env; default `v0.0.1`)
- `GET /temperature` → returns average temperature from openSenseMap (within `SENSEMAP_LOOKBACK_HOURS`, default 1h)

**Run locally**

```bash
cd phase-03
PYTHONPATH=. uvicorn app.main:app --reload
curl -s http://127.0.0.1:8000/version
```

```bash
cd phase-03
docker build -t phase3/api:latest .
docker run --rm -p 8000:8000 -e APP_VERSION="v0.0.1" phase3/api:latest
```

```bash
cd phase-03
PYTHONPATH=. pytest -q
```

Config

- APP_VERSION – version string
- SENSEMAP_LOOKBACK_HOURS – time window in hours for temperature (default: 1)
- SENSEMAP_BASE_URL, HTTP_TIMEOUT – networking settings
