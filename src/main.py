"""
Main pipeline — integrates LLM parsing, KG query, source matching, and download.
"""
from pathlib import Path
from typing import Optional, List
from .llm_parser import LLMParser
from .kg_query import KnowledgeGraphQuery
from .models import QueryParams
from .matcher import DataSourceMatcher, NoSourceFoundError
from .datasources.registry import registry


class GeoDataAcquirer:
    """Geographic data acquirer — supports admin boundaries and multi-source data."""

    def __init__(self, kg_path: str, register_plugins: bool = True):
        print("=" * 60)
        print("Initializing GeoData-Acquirer...")
        print("=" * 60)

        self.kg_path = kg_path
        self.llm_parser = LLMParser()
        self.kg_query = KnowledgeGraphQuery(kg_path)
        self.matcher = DataSourceMatcher()
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

        if register_plugins:
            self._init_plugins()

        print("=" * 60)
        print("[OK] Initialization complete!")
        print("=" * 60)

    def _init_plugins(self):
        """Register all available data source plugins."""
        from .datasources.admin_boundary import AdminBoundarySource
        from .datasources.osm import OSMource
        from .datasources.open_meteo import OpenMeteoSource

        self.admin_source = AdminBoundarySource(kg_path=self.kg_path)
        OSMource()
        OpenMeteoSource()

    def process(self, user_input: str, force_source: Optional[str] = None) -> str:
        """
        Main processing: LLM parse -> KG resolve -> source matching -> download.

        Args:
            user_input: Natural language query.
            force_source: If set, skip matching and use this source name directly.

        Returns:
            Output file path.
        """
        print(f"\n{'=' * 60}")
        print(f"User input: {user_input}")
        print(f"{'=' * 60}\n")

        # Step 1: Parse user input
        print("Step 1: LLM parsing...")
        parsed = self.llm_parser.parse(user_input)
        query = QueryParams(**parsed)
        print(f"  [OK] Region: {query.region}")
        print(f"  [OK] Data type: {query.data_type}")
        if query.temporal and query.temporal.start:
            print(f"  [OK] Temporal: {query.temporal.start} ~ {query.temporal.end}")
        print()

        # Step 2: Resolve region via knowledge graph
        if query.region and not query.region_code:
            admin_info = self.kg_query.get_admin_info(query.region)
            if admin_info:
                query.region_code = admin_info["code"]
                query.region_level = admin_info["level"]
                print(f"Step 2: KG resolved -> code={query.region_code}, level={query.region_level}\n")

        # Step 3: Match data source
        print("Step 3: Matching data source...")
        if force_source:
            source = registry.get_source(force_source)
            if not source:
                raise ValueError(f"Unknown source: {force_source}")
            score = 1.0
        else:
            source, score = self.matcher.get_best_source(query)

        meta = source.get_metadata()
        print(f"  [OK] Source: {meta.name} (score: {score:.2f})")
        print(f"  [OK] Description: {meta.description}\n")

        # Step 4: Search for datasets
        print("Step 4: Searching...")
        results = source.search(query)
        if not results:
            raise NoSourceFoundError(
                f"Source '{meta.name}' found no matching data for query"
            )
        print(f"  [OK] Found {len(results)} result(s)\n")

        # Step 5: Download
        print("Step 5: Downloading...")
        best_result = results[0]
        download_result = source.download(best_result, str(self.output_dir))

        print(f"  [OK] Downloaded: {download_result.local_path}")
        print(f"  [OK] Size: {download_result.size_bytes} bytes\n")

        print(f"{'=' * 60}")
        print(f"[SUCCESS] Output: {download_result.local_path}")
        print(f"{'=' * 60}\n")

        return download_result.local_path

    def list_available_sources(self) -> List[dict]:
        """Return metadata for all registered sources."""
        return [s.get_metadata().model_dump() for s in registry.list_sources()]

    def close(self):
        if hasattr(self, 'admin_source'):
            self.admin_source.close()
