"""
Admin boundary data source — wraps the existing KG query + PostGIS pipeline
as a GeoDataSource plugin.
"""
import json
import os
from typing import List
from .base import GeoDataSource
from .registry import registry
from ..models import QueryParams, SearchResult, DownloadResult, DataSourceMeta


class AdminBoundarySource(GeoDataSource):
    """Chinese administrative boundaries via PostGIS + knowledge graph."""

    def __init__(self, kg_path: str):
        from ..kg_query import KnowledgeGraphQuery
        from ..db_connector import DBConnector

        self.kg = KnowledgeGraphQuery(kg_path)
        self.db = DBConnector()
        registry.register(self)

    def can_handle(self, query: QueryParams) -> bool:
        if query.data_type != "boundary":
            return False
        if not query.region:
            return False
        admin_info = self.kg.get_admin_info(query.region)
        return admin_info is not None

    def search(self, query: QueryParams) -> List[SearchResult]:
        admin_info = self.kg.get_admin_info(query.region)
        if not admin_info:
            return []
        return [SearchResult(
            source_name="admin_boundary",
            match_score=1.0,
            metadata={
                "region": query.region,
                "code": admin_info["code"],
                "level": admin_info["level"],
            }
        )]

    def download(self, result: SearchResult, output_path: str) -> DownloadResult:
        code = result.metadata["code"]
        level = result.metadata["level"]
        region = result.metadata["region"]

        table = self.kg.determine_table(code, level)
        code_field = self.kg.get_code_field(table)
        geometry = self.db.get_boundary(table, code, code_field)

        if not geometry:
            raise ValueError(f"No boundary found for code {code} in table {table}")

        feature = {
            "type": "Feature",
            "properties": {
                "name": region,
                "code": code,
                "level": level,
            },
            "geometry": geometry,
        }

        filename = f"{region}_boundary.geojson"
        filepath = os.path.join(output_path, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(feature, f, ensure_ascii=False, indent=2)

        return DownloadResult(
            local_path=filepath,
            format="GeoJSON",
            size_bytes=os.path.getsize(filepath),
            metadata={"region": region, "code": code, "level": level},
        )

    def get_metadata(self) -> DataSourceMeta:
        return DataSourceMeta(
            name="admin_boundary",
            description="Chinese administrative boundaries (PostGIS, 37,905 regions)",
            coverage="China",
            data_types=["boundary"],
            requires_auth=True,
            quality_score=0.95,
            access_method="PostGIS",
        )

    def close(self):
        self.db.close()
