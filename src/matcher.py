"""
Data source matching engine — scores and ranks compatible sources for a query.
"""
from typing import List, Tuple
from .models import QueryParams
from .datasources.registry import registry
from .datasources.base import GeoDataSource


class NoSourceFoundError(Exception):
    """Raised when no data source can handle a query."""
    pass


class DataSourceMatcher:
    """Matches queries to the best data source(s) based on capability and quality."""

    WEIGHTS = {
        "quality": 0.40,
        "auth_penalty": 0.20,
        "coverage": 0.20,
        "resolution": 0.20,
    }

    def match(self, query: QueryParams, top_k: int = 3) -> List[Tuple[GeoDataSource, float]]:
        """Find top-k matching data sources for a query, ranked by score descending."""
        candidates = []
        for source in registry.find_matching(query):
            score = self._score(source, query)
            candidates.append((source, score))

        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[:top_k]

    def get_best_source(self, query: QueryParams) -> Tuple[GeoDataSource, float]:
        """Return the single best source and its score. Raises NoSourceFoundError if none."""
        matches = self.match(query, top_k=1)
        if not matches:
            raise NoSourceFoundError(
                f"No data source found for query. data_type={query.data_type}, region={query.region}"
            )
        return matches[0]

    def _score(self, source: GeoDataSource, query: QueryParams) -> float:
        meta = source.get_metadata()
        score = 0.0

        score += self.WEIGHTS["quality"] * meta.quality_score
        score += self.WEIGHTS["auth_penalty"] * (1.0 if not meta.requires_auth else 0.3)

        coverage_score = {"Global": 1.0, "China": 0.8, "Regional": 0.5}
        score += self.WEIGHTS["coverage"] * coverage_score.get(meta.coverage, 0.3)

        score += self.WEIGHTS["resolution"] * 0.7

        return min(score, 1.0)
