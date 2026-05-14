"""
Shared Pydantic models for GeoData-Acquirer.
Used by parser, data sources, matcher, and downloader.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float


class TemporalRange(BaseModel):
    start: Optional[str] = None
    end: Optional[str] = None


class QueryParams(BaseModel):
    region: Optional[str] = Field(default=None, description="Place name, e.g. 武汉市")
    region_code: Optional[str] = Field(default=None, description="Admin code resolved from KG")
    region_level: Optional[str] = Field(default=None, description="Admin level from KG")
    data_type: Optional[str] = Field(
        default=None,
        description="Data type: boundary, road, building, poi, landuse, elevation, weather, climate, population, imagery, unknown"
    )
    temporal: Optional[TemporalRange] = None
    spatial_resolution: Optional[str] = Field(default=None, description="e.g. 30m, 1km")
    format: Optional[str] = Field(default=None, description="Desired output: GeoJSON, Shapefile, GeoTIFF, CSV, NetCDF")
    raw_input: str = Field(default="", description="Original user input")

    class Config:
        extra = "allow"


class DataSourceMeta(BaseModel):
    name: str
    description: str
    coverage: str = "Global"
    data_types: List[str] = Field(default_factory=list)
    requires_auth: bool = False
    quality_score: float = 0.5
    access_method: str = "Unknown"


class SearchResult(BaseModel):
    source_name: str
    match_score: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    download_url: Optional[str] = None


class DownloadResult(BaseModel):
    local_path: str
    format: str = "unknown"
    size_bytes: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
