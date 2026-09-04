def predict_risk(rainfall, soil_moisture, slope, historical_risk):
    """
    Explainable landslide risk prediction model.

    Inputs:
    - rainfall: recent rainfall intensity (mm)
    - soil_moisture: soil moisture percentage
    - slope: terrain slope in degrees
    - historical_risk: historical landslide risk (0 to 1)

    Returns:
    - risk_score: 0 to 1
    - risk_level: Low / Moderate / High / Severe
    """

    # Normalize rainfall
    rainfall_score = min(rainfall / 200, 1.0)

    # Normalize soil moisture
    moisture_score = min(soil_moisture / 100, 1.0)

    # Normalize slope
    slope_score = min(slope / 45, 1.0)

    # Calculate weighted risk score
    risk_score = (
        0.35 * rainfall_score
        + 0.25 * moisture_score
        + 0.25 * slope_score
        + 0.15 * historical_risk
    )

    # Keep score between 0 and 1
    risk_score = max(0.0, min(risk_score, 1.0))

    # Determine risk level
    if risk_score < 0.25:
        risk_level = "Low"
    elif risk_score < 0.50:
        risk_level = "Moderate"
    elif risk_score < 0.75:
        risk_level = "High"
    else:
        risk_level = "Severe"

    return {
        "risk_score": round(risk_score, 3),
        "risk_level": risk_level
    }