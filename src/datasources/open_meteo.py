"""
Open-Meteo weather & climate data source. Free, no API key required.
"""
import json
import os
from typing import List
from .base import GeoDataSource
from .registry import registry
from ..downloader import Downloader
from ..models import QueryParams, SearchResult, DownloadResult, DataSourceMeta



class OpenMeteoSource(GeoDataSource):
    """Open-Meteo free weather & climate API."""

    BASE_URL = "https://api.open-meteo.com/v1"

    ENDPOINTS = {
        "weather": "forecast",
        "climate": "climate",
        "air_quality": "air-quality",
    }

    def __init__(self):
        self.downloader = Downloader(max_retries=3, timeout=30, show_progress=False)
        registry.register(self)

    def can_handle(self, query: QueryParams) -> bool:
        return query.data_type in ("weather", "climate", "air_quality")

    # Valid daily variables for the forecast endpoint
    DAILY_WEATHER_VARS = [
        "temperature_2m_max", "temperature_2m_min",
        "precipitation_sum", "wind_speed_10m_max",
    ]

    # Valid daily variables for the climate endpoint
    DAILY_CLIMATE_VARS = [
        "temperature_2m_mean", "precipitation_sum",
        "temperature_2m_max", "temperature_2m_min",
    ]

    # Valid current variables for air quality
    CURRENT_AQ_VARS = ["pm2_5", "pm10", "nitrogen_dioxide", "ozone"]

    def search(self, query: QueryParams) -> List[SearchResult]:
        if query.data_type == "weather":
            available_vars = self.DAILY_WEATHER_VARS
        elif query.data_type == "climate":
            available_vars = self.DAILY_CLIMATE_VARS
        else:
            available_vars = self.CURRENT_AQ_VARS

        return [SearchResult(
            source_name="open_meteo",
            match_score=0.90,
            metadata={
                "available_variables": available_vars,
                "endpoint": self.ENDPOINTS.get(query.data_type, "forecast"),
                "region": query.region,
            }
        )]

    def download(self, result: SearchResult, output_path: str) -> DownloadResult:
        # TODO Phase 3: geocode region name to lat/lon via nominatim or admin boundary centroid
        lat = result.metadata.get("latitude", 30.5928)
        lon = result.metadata.get("longitude", 114.3055)

        endpoint = result.metadata["endpoint"]
        url = f"{self.BASE_URL}/{endpoint}"

        params = {
            "latitude": lat,
            "longitude": lon,
            "timezone": "Asia/Shanghai",
        }

        if endpoint == "forecast":
            params["daily"] = result.metadata.get("available_variables", [])
            params["forecast_days"] = 7
        elif endpoint == "climate":
            params["daily"] = result.metadata.get("available_variables", [])

        if endpoint == "air-quality":
            params["current"] = result.metadata.get("available_variables", [])

        data = self.downloader.download_json(url, params=params)

        label = result.metadata.get("region", f"{lat}_{lon}")
        filename = f"weather_{label}.json"
        filepath = os.path.join(output_path, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return DownloadResult(
            local_path=filepath,
            format="JSON",
            size_bytes=os.path.getsize(filepath),
            metadata={"source": "open-meteo", "endpoint": endpoint},
        )

    def get_metadata(self) -> DataSourceMeta:
        return DataSourceMeta(
            name="open_meteo",
            description="Open-Meteo free weather & climate API",
            coverage="Global",
            data_types=["weather", "climate", "air_quality"],
            requires_auth=False,
            quality_score=0.88,
            access_method="REST API",
        )
