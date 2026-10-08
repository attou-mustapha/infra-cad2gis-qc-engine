-- Enable PostGIS & Topology extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Schema for CAD Ingestion & QC
CREATE SCHEMA IF NOT EXISTS cad_staging;
CREATE SCHEMA IF NOT EXISTS cad_qc;
