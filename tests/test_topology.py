"""Unit tests for CAD2GIS topology validator."""

import pytest
import geopandas as gpd
from shapely.geometry import LineString, Point
from cad2gis_qc.topology import TopologyValidator
from cad2gis_qc.models import AnomalyType


def test_undershoot_detection():
    # Two lines that almost touch (0.2m gap)
    line1 = LineString([(0, 0), (10, 0)])
    line2 = LineString([(10.2, 0), (20, 0)])  # 0.2m gap

    gdf = gpd.GeoDataFrame(
        [{"id": 1, "geometry": line1}, {"id": 2, "geometry": line2}],
        crs="EPSG:32188"
    )

    validator = TopologyValidator(tolerance_meters=0.5)
    anomalies = validator.validate_linear_network(gdf)

    # Should detect undershoot candidate
    undershoots = [a for a in anomalies if a.anomaly_type == AnomalyType.UNDERSHOOT]
    assert len(undershoots) >= 1
