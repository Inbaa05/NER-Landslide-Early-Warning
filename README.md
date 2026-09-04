# NER Landslide Sentinel

A software-only prototype for the SIH problem statement **“AI-Based early warning and landslide Risk Monitoring System in NER”**.

## What this prototype implements
- Interactive NER GIS dashboard with risk zones and road/village context.
- Real-time/future rainfall retrieval from Open-Meteo.
- Dynamic rainfall trigger using the source document's formula:
  `Rtrigger = w1*Rpast_3days + w2*Rcurrent_24h + w3*Rforecast_24h`
- Four risk levels: Low, Moderate, High, Severe.
- Explainable risk cards showing rainfall, slope, soil-moisture proxy and forecast contribution.
- Geo-tagged field-report form with browser geolocation and photo attachment.
- Offline-first report queue using localStorage and automatic retry.
- Multilingual UI seed for English, Hindi and Assamese.
- Emergency-priority list for vulnerable communities.
- REST API with FastAPI.
- Production-oriented PostGIS schema.
- Docker and Render deployment configuration.
- Automated backend tests and CI workflow.

> Important: this is a decision-support prototype, not a certified disaster-warning system. The ML layer is represented by an explainable baseline scoring engine so the application remains runnable without private model files. A production system should train and validate an ML model on authoritative historical landslide data before issuing operational warnings.

## Run locally

### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Open API docs at `http://localhost:8000/docs`.

### Frontend
From the project root:
```bash
cd frontend
python -m http.server 5500
```
Open `http://localhost:5500`.

The frontend defaults to `http://localhost:8000`. Change `API_BASE` in `frontend/app.js` if required.

## Docker
```bash
docker compose up --build
```

## Production deployment
### Backend on Render
1. Create a new Web Service from this repository.
2. Runtime: Docker.
3. Dockerfile: `backend/Dockerfile`.
4. Expose port 8000.
5. Set `CORS_ORIGINS` to the deployed frontend URL.
6. Attach a managed PostgreSQL/PostGIS database for production.
7. Configure weather/data-provider credentials where required by the final integrations.

### Frontend
The `frontend/` folder can be deployed as a static site on Vercel, Netlify, Cloudflare Pages, GitHub Pages, or an object-storage CDN.

## Production data integrations from the supplied SIH architecture
The supplied document calls for:
- IMD / Open-Meteo / ECMWF weather.
- NASA SMAP or Sentinel-1 soil-moisture data.
- SRTM / ALOS PALSAR DEM-derived slope.
- GSI Bhukosh / NASA Global Landslide Catalog / ISRO Bhuvan historical events.
- PostGIS for spatial data.
- Leaflet / Mapbox / OpenLayers and GeoServer for GIS.
- SMS, push and IVR alert channels.
- Celery/Airflow ingestion.
- MLflow/Kubeflow retraining.
- Docker/Kubernetes for scalable deployment.

This repository implements the software-facing foundation and leaves credentials, provider contracts, authoritative datasets, and operational approval as deployment-time configuration.

## API
- `GET /api/health`
- `GET /api/zones`
- `GET /api/risk?lat=26.14&lon=91.74`
- `POST /api/reports`
- `GET /api/priority`
- `GET /api/forecast?lat=26.14&lon=91.74`

Interactive OpenAPI documentation is available at `/docs`.

## Testing
```bash
cd backend
pip install -r requirements.txt
pytest -q
```

## Architecture
```text
Weather / Satellite / DEM / Historical Events
                    |
             ETL / Scheduler
                    |
               PostGIS DB
                    |
        +-----------+-----------+
        |                       |
   Risk Engine             GIS Services
        |                       |
        +-----------+-----------+
                    |
             FastAPI Gateway
              /           \
       Web Dashboard    Field PWA
              \           /
            Alert Dispatcher
          SMS / Push / IVR
```

## UAT acceptance criteria
1. Dashboard loads on desktop and mobile.
2. Map displays risk zones and responds to zone selection.
3. Forecast values update from the weather API when available.
4. A field report captures location and can be queued offline.
5. Queued reports are retried when connectivity returns.
6. Risk explanation identifies the dominant factors.
7. UI remains keyboard navigable and uses accessible labels.
8. API returns valid JSON and appropriate HTTP status codes.
9. Production deployment uses HTTPS, restricted CORS, secrets, logging and a managed PostGIS database.
