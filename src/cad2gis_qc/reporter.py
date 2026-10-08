"""Report generation for QC anomalies: GeoJSON layer and HTML interactive dashboard."""

import json
from pathlib import Path
from typing import List
from shapely import wkt
import geopandas as gpd
from jinja2 import Template
from .models import QCAnomaly, QCReportSummary


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CAD2GIS Topology QC Report</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 2rem; }
        .container { max-width: 1100px; margin: 0 auto; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 1.5rem; margin-bottom: 2rem; }
        .score-card { background: #1e293b; border-radius: 12px; padding: 1.5rem; display: flex; gap: 2rem; margin-bottom: 2rem; }
        .score-box { text-align: center; }
        .score-val { font-size: 2.5rem; font-weight: 700; color: #38bdf8; }
        .error-badge { background: #ef4444; color: white; padding: 0.2rem 0.6rem; border-radius: 4px; font-weight: 600; font-size: 0.8rem; }
        .warn-badge { background: #f59e0b; color: white; padding: 0.2rem 0.6rem; border-radius: 4px; font-weight: 600; font-size: 0.8rem; }
        table { width: 100%; border-collapse: collapse; margin-top: 1rem; background: #1e293b; border-radius: 8px; overflow: hidden; }
        th, td { padding: 0.85rem 1rem; text-align: left; border-bottom: 1px solid #334155; }
        th { background: #0f172a; color: #94a3b8; font-size: 0.85rem; text-transform: uppercase; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>🚇 CAD2GIS Topology QC Engine</h1>
                <p>Inspection Report: <code>{{ summary.file_path }}</code></p>
            </div>
            <div>
                <span style="color: #94a3b8;">Execution: {{ "%.2f"|format(summary.execution_time_seconds) }}s</span>
            </div>
        </div>

        <div class="score-card">
            <div class="score-box">
                <div class="score-val">{{ "%.1f"|format(summary.quality_score) }}%</div>
                <div style="color: #94a3b8;">Quality Index</div>
            </div>
            <div class="score-box">
                <div class="score-val" style="color: #f8fafc;">{{ summary.total_features }}</div>
                <div style="color: #94a3b8;">Total Features</div>
            </div>
            <div class="score-box">
                <div class="score-val" style="color: #22c55e;">{{ summary.valid_features }}</div>
                <div style="color: #94a3b8;">Valid Features</div>
            </div>
            <div class="score-box">
                <div class="score-val" style="color: #ef4444;">{{ summary.invalid_features }}</div>
                <div style="color: #94a3b8;">Anomalies Detected</div>
            </div>
        </div>

        <h2>Detailed Anomaly Log</h2>
        <table>
            <thead>
                <tr>
                    <th>Type</th>
                    <th>Severity</th>
                    <th>Feature ID</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
                {% for a in summary.anomalies %}
                <tr>
                    <td><code>{{ a.anomaly_type }}</code></td>
                    <td>
                        <span class="{{ 'error-badge' if a.severity in ['ERROR', 'CRITICAL'] else 'warn-badge' }}">{{ a.severity }}</span>
                    </td>
                    <td>#{{ a.feature_id or 'N/A' }}</td>
                    <td>{{ a.description }}</td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="4" style="text-align: center; color: #22c55e; padding: 2rem;">
                        ✅ Zero topological defects detected. Dataset is 100% compliant!
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
"""


def export_geojson_anomalies(anomalies: List[QCAnomaly], output_path: Path):
    """Save anomalies as a GeoJSON layer for visual inspection in QGIS/ArcGIS."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    features = []
    for a in anomalies:
        try:
            geom = wkt.loads(a.geometry_wkt)
        except Exception:
            continue
        features.append({
            "type": "Feature",
            "geometry": geom.__geo_interface__,
            "properties": {
                "id": a.id,
                "feature_id": a.feature_id,
                "layer_name": a.layer_name,
                "anomaly_type": a.anomaly_type.value,
                "severity": a.severity.value,
                "description": a.description,
                "tolerance": a.tolerance_distance
            }
        })

    geojson_data = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(geojson_data, f, indent=2)


def export_html_report(summary: QCReportSummary, output_path: Path):
    """Generate standalone HTML QC summary."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    template = Template(HTML_TEMPLATE)
    html_content = template.render(summary=summary)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
