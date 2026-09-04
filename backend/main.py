from risk_model import predict_risk
from datetime import datetime, timezone
from typing import Optional
import math
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="NER Landslide Sentinel API",
    version="1.0.0",
    description="Software-only landslide risk monitoring prototype for the North Eastern Region."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to deployed frontend origin in production.
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Demo zones keep the application runnable without a proprietary GIS dataset.
ZONES = [
    {"id":"NER-01","name":"Guwahati Hills","state":"Assam","lat":26.1445,"lon":91.7362,"slope":31,"population":18000,"road":"NH-27"},
    {"id":"NER-02","name":"Shillong South","state":"Meghalaya","lat":25.5788,"lon":91.8933,"slope":38,"population":9200,"road":"NH-6"},
    {"id":"NER-03","name":"Aizawl Ridge","state":"Mizoram","lat":23.7271,"lon":92.7176,"slope":42,"population":7600,"road":"NH-306"},
    {"id":"NER-04","name":"Imphal East Hills","state":"Manipur","lat":24.8170,"lon":93.9368,"slope":29,"population":12400,"road":"NH-2"},
    {"id":"NER-05","name":"Agartala Fringe","state":"Tripura","lat":23.8315,"lon":91.2868,"slope":19,"population":15300,"road":"NH-8"},
    {"id":"NER-06","name":"Gangtok Approach","state":"Sikkim","lat":27.3389,"lon":88.6065,"slope":46,"population":6400,"road":"NH-10"},
]

class Report(BaseModel):
    latitude: float
    longitude: float
    category: str = Field(pattern="^(crack|slope-movement|blocked-road|rockfall|other)$")
    description: str = Field(min_length=3, max_length=1000)
    timestamp: Optional[str] = None

def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))

def risk_from_inputs(rain_24: float, rain_72: float, forecast_24: float, slope: float, soil_proxy: float):
    # Explainable software baseline. Replace with validated RF/XGBoost/LSTM in production.
    rain_component = clamp((rain_24 * 0.50 + rain_72 * 0.20 + forecast_24 * 0.30) / 120.0)
    slope_component = clamp(slope / 50.0)
    score = clamp(0.58 * rain_component + 0.27 * slope_component + 0.15 * soil_proxy)
    if score >= 0.75:
        level = "Severe"
    elif score >= 0.55:
        level = "High"
    elif score >= 0.32:
        level = "Moderate"
    else:
        level = "Low"
    return round(score, 3), level, round(rain_component, 3), round(slope_component, 3)

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "ner-landslide-sentinel", "utc": datetime.now(timezone.utc).isoformat()}

@app.get("/api/zones")
def zones():
    return {"zones": ZONES}

@app.get("/api/priority")
def priority():
    scored = []
    for z in ZONES:
        score, level, _, _ = risk_from_inputs(55, 110, 48, z["slope"], 0.58)
        priority = score * (1 + math.log10(z["population"] + 10) / 10)
        scored.append({**z, "risk_score": score, "risk_level": level, "priority": round(priority, 3)})
    return {"items": sorted(scored, key=lambda x: x["priority"], reverse=True)}

@app.get("/api/forecast")
async def forecast(lat: float, lon: float):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=precipitation,rain,precipitation_probability,relative_humidity_2m"
        "&forecast_days=7&timezone=auto"
    )

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url)
            r.raise_for_status()
            return r.json()

    except Exception as exc:
        print(f"Weather provider unavailable: {exc}")

        # Demo fallback data when the weather API is unavailable
        return {
            "hourly": {
                "rain": [0.5] * 169,
                "precipitation": [0.5] * 169,
                "precipitation_probability": [30] * 169,
                "relative_humidity_2m": [70] * 169
            },
            "fallback": True
        }    

@app.get("/api/risk")
async def risk(
    lat: float,
    lon: float,
    slope: float = 30,
    soil_moisture: float = 55
):
    data = await forecast(lat, lon)

    rain = data["hourly"]["rain"]

    current = float(rain[0] or 0)

    forecast_24 = sum(
        float(x or 0) for x in rain[1:25]
    )

    # Demo estimate for recent rainfall.
    # Production version should use historical rainfall observations.
    past_72 = min(forecast_24 * 1.7, 180.0)

    # Use the AI risk model
    prediction = predict_risk(
        rainfall=past_72,
        soil_moisture=soil_moisture,
        slope=slope,
        historical_risk=0.6
    )

    return {
        "lat": lat,
        "lon": lon,
        "risk_score": prediction["risk_score"],
        "risk_level": prediction["risk_level"],
        "current_rain_mm_h": round(current, 2),
        "rain_24h_forecast_mm": round(forecast_24, 2),
        "rain_72h_proxy_mm": round(past_72, 2),
        "slope_degrees": slope,
        "soil_moisture_proxy": soil_moisture,
        "explanation": {
            "rainfall_contribution": round(
                min(past_72 / 200, 1.0) * 0.35, 3
            ),
            "soil_moisture_contribution": round(
                min(soil_moisture / 100, 1.0) * 0.25, 3
            ),
            "slope_contribution": round(
                min(slope / 45, 1.0) * 0.25, 3
            ),
            "historical_risk_contribution": 0.09,
            "note": "Explainable AI-based prototype prediction."
        },
        "generated_at": datetime.now(timezone.utc).isoformat()
    }