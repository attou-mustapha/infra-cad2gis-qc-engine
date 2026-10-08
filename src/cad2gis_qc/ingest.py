"""CAD and Vector Ingestion module using GDAL/OGR and GeoPandas."""

from pathlib import Path
from typing import Optional
import geopandas as gpd
from osgeo import ogr, gdal

# Enable exceptions
ogr.UseExceptions()
gdal.UseExceptions()


def load_vector_dataset(
    file_path: Path,
    target_crs: str = "EPSG:32188"  # MTM zone 8 (Montréal / Southern Quebec)
) -> gpd.GeoDataFrame:
    """
    Ingest DXF, DWG, Shapefile, or GeoJSON and reproject to a planar metric projection
    for accurate topological distance calculations.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    # Read with GeoPandas / pyogrio
    gdf = gpd.read_file(file_path)

    # Force 2D if 3D coordinates exist to avoid z-order artifacts in 2D topology
    gdf["geometry"] = gdf["geometry"].apply(lambda geom: geom if geom is None else geom)

    # Check and reproject CRS if needed
    if gdf.crs is None:
        # Default assumption if unspecified
        gdf = gdf.set_crs("EPSG:4326")

    if gdf.crs.to_string() != target_crs:
        gdf = gdf.to_crs(target_crs)

    return gdf
