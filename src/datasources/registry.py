"""
Data source registry — singleton that tracks all available GeoDataSource plugins.
"""
from typing import List, Optional
from .base import GeoDataSource
from ..models import DataSourceMeta


class DataSourceRegistry:
    """Singleton registry for all GeoDataSource plugins."""

    _instance: Optional["DataSourceRegistry"] = None

    def __new__(cls) -> "DataSourceRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._sources = []
        return cls._instance

    def register(self, source: GeoDataSource) -> None:
        """Add a data source to the registry."""
        self._sources.append(source)

    def list_sources(self) -> List[GeoDataSource]:
        """Return all registered sources."""
        return list(self._sources)

    def get_source(self, name: str) -> Optional[GeoDataSource]:
        """Get a source by name."""
        for s in self._sources:
            if s.get_metadata().name == name:
                return s
        return None

    def find_matching(self, query) -> List[GeoDataSource]:
        """Return all sources where can_handle(query) is True."""
        return [s for s in self._sources if s.can_handle(query)]


# Module-level singleton
registry = DataSourceRegistry()
