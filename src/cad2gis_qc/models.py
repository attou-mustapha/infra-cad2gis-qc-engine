"""Data models for CAD2GIS Quality Control anomalies and reports."""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class SeverityLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AnomalyType(str, Enum):
    UNDERSHOOT = "UNDERSHOOT"
    OVERSHOOT = "OVERSHOOT"
    DUPLICATE_GEOMETRY = "DUPLICATE_GEOMETRY"
    SELF_INTERSECTION = "SELF_INTERSECTION"
    DANGLING_NODE = "DANGLING_NODE"
    UNCLOSED_RING = "UNCLOSED_RING"
    INVALID_DIMENSION = "INVALID_DIMENSION"


class QCAnomaly(BaseModel):
    id: str
    feature_id: Optional[str] = None
    layer_name: str
    anomaly_type: AnomalyType
    severity: SeverityLevel
    description: str
    geometry_wkt: str
    tolerance_distance: Optional[float] = None
    properties: Dict[str, Any] = Field(default_factory=dict)


class QCReportSummary(BaseModel):
    file_path: str
    total_features: int
    valid_features: int
    invalid_features: int
    quality_score: float = Field(..., description="Score from 0.0 to 100.0%")
    anomalies_by_type: Dict[str, int]
    anomalies_by_severity: Dict[str, int]
    execution_time_seconds: float
    anomalies: List[QCAnomaly] = Field(default_factory=list)
