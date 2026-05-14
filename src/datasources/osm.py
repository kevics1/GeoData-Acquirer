"""
OpenStreetMap data source via Overpass API.
"""
import json
import os
from typing import List
from .base import GeoDataSource
from .registry import registry
from ..downloader import Downloader
from ..models import QueryParams, SearchResult, DownloadResult, DataSourceMeta


class OSMource(GeoDataSource):
    """OpenStreetMap vector data via Overpass API."""

    OVERPASS_URL = "https://overpass-api.de/api/interpreter"

    OSM_TAG_MAP = {
        "road": '["highway"]',
        "building": '["building"]',
        "waterway": '["waterway"]',
        "landuse": '["landuse"]',
        "poi": '["amenity"]',
    }

    def __init__(self):
        self.downloader = Downloader(max_retries=2, timeout=60, show_progress=False)
        registry.register(self)

    def can_handle(self, query: QueryParams) -> bool:
        return query.data_type in self.OSM_TAG_MAP and query.region is not None

    def search(self, query: QueryParams) -> List[SearchResult]:
        if not query.region:
            return []
        return [SearchResult(
            source_name="osm",
            match_score=0.85,
            metadata={
                "region": query.region,
                "data_type": query.data_type,
                "osm_tag": self.OSM_TAG_MAP.get(query.data_type, ""),
            }
        )]

    def download(self, result: SearchResult, output_path: str) -> DownloadResult:
        region = result.metadata["region"]
        osm_tag = result.metadata["osm_tag"]

        overpass_query = self._build_query(region, osm_tag)
        data = self.downloader.download_json(
            self.OVERPASS_URL,
            params={"data": overpass_query},
            headers={"Accept": "application/json", "User-Agent": "GeoData-Acquirer/1.0"}
        )

        geojson = self._osm_to_geojson(data)

        safe_type = result.metadata.get("data_type", "osm")
        filename = f"{region}_{safe_type}.geojson"
        filepath = os.path.join(output_path, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(geojson, f, ensure_ascii=False)

        return DownloadResult(
            local_path=filepath,
            format="GeoJSON",
            size_bytes=os.path.getsize(filepath),
            metadata={"element_count": len(geojson.get("features", []))},
        )

    def get_metadata(self) -> DataSourceMeta:
        return DataSourceMeta(
            name="osm",
            description="OpenStreetMap vector data (Overpass API)",
            coverage="Global",
            data_types=["road", "building", "poi", "landuse", "waterway"],
            requires_auth=False,
            quality_score=0.85,
            access_method="REST API (Overpass)",
        )

    def _build_query(self, region: str, osm_tag: str) -> str:
        return f"""[out:json][timeout:60];
area["name"="{region}"]->.searchArea;
(
  way{osm_tag}(area.searchArea);
  relation{osm_tag}(area.searchArea);
);
out body;
>;
out skel qt;"""

    def _osm_to_geojson(self, osm_data: dict) -> dict:
        features = []
        for elem in osm_data.get("elements", []):
            if elem.get("type") == "node" and "lat" in elem and "lon" in elem:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [elem["lon"], elem["lat"]],
                    },
                    "properties": elem.get("tags", {}),
                })
            elif elem.get("type") == "way" and "geometry" in elem:
                coords = [[p["lon"], p["lat"]] for p in elem["geometry"]]
                if len(coords) < 2:
                    continue
                is_closed = (coords[0][0] == coords[-1][0] and
                             coords[0][1] == coords[-1][1])
                if is_closed and len(coords) >= 4:
                    geom = {"type": "Polygon", "coordinates": [coords]}
                else:
                    geom = {"type": "LineString", "coordinates": coords}
                features.append({
                    "type": "Feature",
                    "geometry": geom,
                    "properties": elem.get("tags", {}),
                })
        return {"type": "FeatureCollection", "features": features}
