# Technical report — NER Landslide Sentinel

## 1. Source requirements extracted
The supplied architecture document describes a North Eastern Region landslide system that should collect rainfall, soil moisture, satellite imagery, terrain/slope data and historical landslide records; use AI/ML for high-risk-zone prediction; issue alerts; provide GIS visualization; accept geo-tagged citizen/field uploads; provide risk, road, weather and response dashboards; support multilingual and low-network/offline operation. It also describes a software-only route using satellite-derived soil moisture instead of physical sensors.

## 2. Solution mapping
| Source requirement | Prototype implementation |
|---|---|
| Real-time GIS dashboard | Leaflet map + selectable NER zones |
| Risk heatmaps | Zone markers + risk states; production-ready extension point for vector tiles |
| AI/ML engine | Explainable baseline scoring engine; ML replacement interface documented |
| Weather integration | Open-Meteo forecast API |
| Satellite soil moisture | Production data source specified; proxy used in runnable demo |
| DEM/slope | Zone slope input; production PostGIS/DEM pipeline documented |
| Historical landslides | Production ingestion target documented |
| Geo-tagged reporting | Browser geolocation + field report form |
| Offline sync | localStorage queue + online retry |
| Multilingual notifications | UI language seed; notification service is deployment-stage integration |
| Emergency prioritisation | risk + population ranking |
| Cloud architecture | Docker + Render config + CI |
| Spatial DB | PostGIS schema |
| Alerts | API boundary prepared; SMS/push/IVR is production integration |
| MLOps | Extension point for MLflow/Kubeflow in source document |

## 3. Innovative additions
### Explainable risk cards
Instead of only showing a red/orange label, the UI exposes rainfall and slope contribution. This improves operator trust and makes demonstrations easier to audit.

### Offline field intelligence
Reports are queued locally when the network is unavailable and retried when connectivity returns. This directly targets remote-area constraints.

### Emergency priority score
Zones are ranked using risk and population, creating an actionable list rather than a passive map.

### Software-only deployment path
The system can be demonstrated without physical sensors, while preserving explicit interfaces for satellite soil moisture, DEM and historical landslide feeds.

## 4. Security design
Production requirements:
- HTTPS everywhere.
- OAuth2/JWT for officials.
- Role-based access control.
- Restrict CORS to known frontend origins.
- Validate file type/size and malware-scan uploads.
- Store media in private object storage with signed URLs.
- Encrypt secrets with cloud secret management.
- Rate-limit public reporting endpoints.
- Audit administrative actions.
- Avoid exposing citizen phone numbers in client-side payloads.
- Apply retention and deletion policies to location/media data.

## 5. Scalability
FastAPI can be horizontally scaled behind a load balancer. PostgreSQL/PostGIS handles spatial queries. Object storage handles media. A queue such as Celery can decouple ingestion and alert dispatch. Kubernetes is appropriate once workload and operational complexity justify it.

## 6. Testing strategy
### Unit
- Risk score boundaries.
- Risk level classification.
- Input validation.

### Integration
- API health/zones/report endpoints.
- Weather-provider failure handling.
- Offline queue retry.

### User acceptance
- Authority can identify high-risk zones within 30 seconds.
- Field reporter can create a geo-tagged report in under 60 seconds.
- App remains usable with network disconnected.
- Risk explanation is understandable without ML expertise.
- Keyboard navigation and readable labels work on desktop/mobile.

## 7. Important operational limitation
The supplied document proposes validated AI/ML prediction and external authoritative datasets. This prototype intentionally does not claim that a heuristic is a validated landslide predictor. Before operational warnings, the model must be trained/evaluated against authoritative regional events, calibrated, monitored for drift, and approved through the responsible disaster-management authority.
