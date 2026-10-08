"""Script to download real transit data from Données Québec (MTMD rail network)."""

import os
from pathlib import Path
import requests

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# MTMD Quebec Railway Network GeoJSON endpoint
MTMD_RAILWAY_URL = (
    "https://ws.mapserver.transports.gouv.qc.ca/swtq?"
    "service=wfs&version=2.0.0&request=getfeature&"
    "typename=ms:reseau_chfer_qc&outfile=ReseauFerroviaire&"
    "srsname=EPSG:4326&outputformat=geojson"
)

DEST_FILE = DATA_DIR / "reseau_ferroviaire_quebec.geojson"


def download_dataset():
    print(f"📥 Downloading Québec Rail Network from Données Québec / MTMD...")
    print(f"URL: {MTMD_RAILWAY_URL}")
    try:
        response = requests.get(MTMD_RAILWAY_URL, timeout=60, stream=True)
        response.raise_for_status()
        with open(DEST_FILE, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Successfully downloaded to {DEST_FILE} ({DEST_FILE.stat().st_size / 1024:.1f} KB)")
    except Exception as e:
        print(f"⚠️ Direct download failed: {e}")
        print("Note: You can also manually download the GeoJSON/Shapefile from https://www.donneesquebec.ca/recherche/fr/dataset/c2c4f386-a736-4eaa-b5b6-28c3a8f75466")


if __name__ == "__main__":
    download_dataset()
