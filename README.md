# 🚇 Infra CAD2GIS Quality Control & Topology Validation Engine (`infra-cad2gis-qc-engine`)

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![PostGIS](https://img.shields.io/badge/PostGIS-16--3.4-336791.svg)](https://postgis.net/)
[![GDAL/OGR](https://img.shields.io/badge/GDAL%2FOGR-3.8+-brightgreen.svg)](https://gdal.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade, high-performance CLI and Dockerized spatial pipeline designed to bridge the structural gap between CAD engineering drawings (AutoCAD DXF/DWG) and enterprise GIS transit networks. 

Built to address real-world quality control challenges encountered in major Canadian civil engineering and transit infrastructure programs (e.g., Montreal REM, ARTM, Metrolinx Ontario, Transports Québec).

---

## 🎯 Business Problem & Architectural Challenge

In massive transport and civil infrastructure programs, engineering deliverables are submitted by disparate surveying contractors and engineering design teams as CAD files (AutoCAD DXF/DWG) or unstructured GIS exports. 

### The Core Obstacles
1. **Topological Incoherencies ("Spaghetti CAD")**: CAD workflows optimize for visual aesthetics rather than graph connectivity. This results in:
   - **Undershoots & Overshoots**: Tracks or corridors failing to snap to switch points or stations by sub-meter gaps ($0.05\text{m} - 0.5\text{m}$).
   - **Un-noded Intersections**: Rail tracks crossing without topological junction vertices.
   - **Duplicate Overlapping Geometries**: Causing artificial double-counting in network asset inventories.
2. **High Latency & Manual Review Burden**: Quality inspection traditionally relies on manual CAD/QGIS pan-and-scan audits, creating multi-week bottlenecks before contractors can get paid and assets can enter enterprise routing databases (`pgRouting`).
3. **Geodetic & Projection Drift**: CAD files created in local false origin or floating coordinates requiring deterministic reprojection to metric planar systems (e.g., MTM Zone 8 / EPSG:32188 for Greater Montreal).

---

## 💡 Solution Architecture & Technical Implementation

`infra-cad2gis-qc-engine` automates this entire pipeline into a single containerized step:

```
                  ┌──────────────────────────────────────────────┐
                  │           Input Deliverables                 │
                  │  (DXF / DWG / Shapefiles / GeoJSON / ARTM)   │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │    GDAL/OGR Ingestion & Normalization Layer  │
                  │  • Planar metric projection (EPSG:32188)     │
                  │  • 3D to 2D topological flattening          │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │      Parallelized Validation Engines         │
                  │                                              │
                  │  [A] Python / Shapely 2.0 In-Memory Engine   │
                  │      • R-Tree spatial indexing               │
                  │      • Sub-meter endpoint snap candidates    │
                  │                                              │
                  │  [B] PostGIS Topology Engine (SQL-backed)    │
                  │      • ST_Node, ST_Dump, ST_Snap             │
                  │      • Graph cycles & dangling node search   │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │        Automated QC Deliverables             │
                  │  1. Standalone HTML Quality Audit Dashboard  │
                  │  2. GeoJSON Defect Layer (QGIS/ArcGIS ready) │
                  │  3. Sanitized PostGIS Network Table          │
                  └──────────────────────────────────────────────┘
```

---

## 🗺️ Canonical Datasets (Open Data Canada)

This repository includes automated loaders for official Canadian public transit and railway networks:

1. **Réseau Ferroviaire du Québec (MTMD - Transports Québec)**:
   - Official linear tracks, switches, operators, and subdivisions across Quebec.
   - [Données Québec Catalog](https://www.donneesquebec.ca/recherche/fr/dataset/c2c4f386-a736-4eaa-b5b6-28c3a8f75466)
   - Real-time WFS API GeoJSON endpoint integrated in `scripts/download_montreal_transit_data.py`.
2. **STM Lignes & Arrêts (Montréal)**:
   - Bus and Metro lines converted from GTFS to GIS vectors.
   - [Ville de Montréal Open Data](https://donnees.montreal.ca/dataset/stm-traces-des-lignes-de-bus-et-de-metro)
3. **ARTM Équipements Métropolitains**:
   - Major transit nodes, train stations, and bus terminals across Greater Montreal.

---

## 🚀 Quickstart & Usage

### 1. Prerequisites
- Docker & Docker Compose **OR** Python 3.11 with GDAL/GEOS libraries installed.

### 2. Launching with Docker Compose
```bash
# Clone the repository
git clone https://github.com/attou-mustapha/infra-cad2gis-qc-engine.git
cd infra-cad2gis-qc-engine

# Start the PostGIS database and engine container
docker compose up -d
```

### 3. Fetch Official Dataset
```bash
python scripts/download_montreal_transit_data.py
```

### 4. Running Quality Inspection
```bash
# Run CLI validation with 0.5-meter snapping tolerance
python -m cad2gis_qc.cli validate data/raw/reseau_ferroviaire_quebec.geojson \
    --tolerance 0.5 \
    --crs EPSG:32188 \
    --output-dir reports/
```

### 5. Outputs Produced
- `reports/reseau_ferroviaire_quebec_qc_report.html`: Executive quality dashboard with scoring, anomaly breakdown, and execution logs.
- `reports/reseau_ferroviaire_quebec_qc_anomalies.geojson`: Point/Line defect layer classified by severity (`CRITICAL`, `ERROR`, `WARNING`, `INFO`).

---

## 🧪 Testing & CI/CD
```bash
pytest tests/ -v
```

---

## 👨‍💻 Author & Competency Profile
**Mustapha ATTOU**  
*State Engineer in Computer Science (Ingénieur d'État en Informatique)*  
Spatial Database Administrator, GIS Pipeline Architect & Full-Stack Geospatial Developer.  
- GitHub: [@attou-mustapha](https://github.com/attou-mustapha)
- LinkedIn: [attou-mustapha](https://www.linkedin.com/in/attou-mustapha)
- Email: [attou.mustapha.pro@gmail.com](mailto:attou.mustapha.pro@gmail.com)
