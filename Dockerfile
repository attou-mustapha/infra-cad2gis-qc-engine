FROM python:3.11-slim

# System dependencies for GDAL/OGR & GEOS
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

COPY src/ ./src/
COPY scripts/ ./scripts/

CMD ["python", "-m", "cad2gis_qc.cli", "--help"]
