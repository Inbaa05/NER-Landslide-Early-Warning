# API documentation

Base URL: `http://localhost:8000`

## GET /api/health
Health check.

## GET /api/zones
Returns demo NER risk-monitoring zones.

## GET /api/forecast?lat={lat}&lon={lon}
Returns Open-Meteo hourly precipitation/rain and forecast data.

## GET /api/risk?lat={lat}&lon={lon}&slope={degrees}&soil_moisture={0..1}
Calculates the prototype dynamic risk score.

Example:
`/api/risk?lat=26.1445&lon=91.7362&slope=31&soil_moisture=0.58`

## GET /api/priority
Returns zones ranked using risk score and population.

## POST /api/reports
JSON:
```json
{
  "latitude": 26.14,
  "longitude": 91.74,
  "category": "crack",
  "description": "Fresh crack observed near road edge.",
  "timestamp": "2026-09-04T06:30:00Z"
}
```
