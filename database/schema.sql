CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS users (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  phone TEXT,
  language VARCHAR(16) NOT NULL DEFAULT 'en',
  role VARCHAR(32) NOT NULL DEFAULT 'citizen',
  location GEOGRAPHY(POINT,4326),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS risk_zones (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  state TEXT NOT NULL,
  geometry GEOMETRY(POLYGON,4326) NOT NULL,
  risk_score DOUBLE PRECISION NOT NULL,
  risk_level VARCHAR(16) NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_users_location ON users USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_risk_zones_geometry ON risk_zones USING GIST(geometry);

CREATE TABLE IF NOT EXISTS observations (
  id BIGSERIAL PRIMARY KEY,
  source TEXT NOT NULL,
  observed_at TIMESTAMPTZ NOT NULL,
  rainfall_mm DOUBLE PRECISION,
  soil_moisture DOUBLE PRECISION,
  latitude DOUBLE PRECISION,
  longitude DOUBLE PRECISION,
  metadata JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS field_reports (
  id BIGSERIAL PRIMARY KEY,
  reporter_id BIGINT REFERENCES users(id),
  category TEXT NOT NULL,
  description TEXT NOT NULL,
  location GEOGRAPHY(POINT,4326) NOT NULL,
  media_object_key TEXT,
  captured_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  status TEXT NOT NULL DEFAULT 'queued'
);
