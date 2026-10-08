"""Topological validation engine using Shapely and NetworkX."""

from typing import List, Tuple
import geopandas as gpd
from shapely.geometry import Point, LineString, MultiLineString
from shapely.ops import linemerge, unary_union
import networkx as nx
from .models import QCAnomaly, AnomalyType, SeverityLevel


class TopologyValidator:
    """
    Validates topological rules for linear networks (railways, roads, pipelines).
    """

    def __init__(self, tolerance_meters: float = 0.5):
        self.tolerance = tolerance_meters

    def validate_linear_network(
        self,
        gdf: gpd.GeoDataFrame,
        layer_name: str = "transit_network"
    ) -> List[QCAnomaly]:
        anomalies: List[QCAnomaly] = []

        # 1. Check for basic geometry validity (OGC compliance)
        for idx, row in gdf.iterrows():
            geom = row.geometry
            if geom is None or geom.is_empty:
                continue

            if not geom.is_valid:
                anomalies.append(
                    QCAnomaly(
                        id=f"invalid_geom_{idx}",
                        feature_id=str(idx),
                        layer_name=layer_name,
                        anomaly_type=AnomalyType.SELF_INTERSECTION,
                        severity=SeverityLevel.CRITICAL,
                        description=f"OGC geometry validation failure: {geom.is_valid}",
                        geometry_wkt=geom.wkt,
                    )
                )

        # 2. Extract endpoints and check for undershoots / overshoots
        endpoints: List[Tuple[int, str, Point]] = []
        for idx, row in gdf.iterrows():
            geom = row.geometry
            if isinstance(geom, LineString):
                endpoints.append((idx, "start", Point(geom.coords[0])))
                endpoints.append((idx, "end", Point(geom.coords[-1])))
            elif isinstance(geom, MultiLineString):
                for part in geom.geoms:
                    endpoints.append((idx, "start", Point(part.coords[0])))
                    endpoints.append((idx, "end", Point(part.coords[-1])))

        # Spatial index for endpoint proximity checks
        if endpoints:
            points_gdf = gpd.GeoDataFrame(
                [{"idx": e[0], "type": e[1], "geometry": e[2]} for e in endpoints],
                crs=gdf.crs
            )
            sindex = points_gdf.sindex

            # Detect near-misses (potential undershoots within tolerance)
            for i, p_row in points_gdf.iterrows():
                pt = p_row.geometry
                buffer = pt.buffer(self.tolerance)
                possible_matches = list(sindex.intersection(buffer.bounds))
                
                # Check distances
                close_neighbors = []
                for match_idx in possible_matches:
                    if match_idx == i:
                        continue
                    other_pt = points_gdf.iloc[match_idx].geometry
                    dist = pt.distance(other_pt)
                    if 0.0 < dist <= self.tolerance:
                        close_neighbors.append((match_idx, dist))

                if close_neighbors:
                    anomalies.append(
                        QCAnomaly(
                            id=f"undershoot_{i}",
                            feature_id=str(p_row.idx),
                            layer_name=layer_name,
                            anomaly_type=AnomalyType.UNDERSHOOT,
                            severity=SeverityLevel.WARNING,
                            description=f"Dangling endpoint within {close_neighbors[0][1]:.3f}m of another vertex (undershoot/snap candidate)",
                            geometry_wkt=pt.wkt,
                            tolerance_distance=self.tolerance,
                            properties={"target_distance": close_neighbors[0][1]}
                        )
                    )

        return anomalies
