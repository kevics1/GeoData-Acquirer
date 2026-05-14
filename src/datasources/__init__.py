"""
Data source plugins package.
Exports the registry singleton, base class, and all built-in sources.
"""
from .base import GeoDataSource
from .registry import DataSourceRegistry, registry

__all__ = ["GeoDataSource", "DataSourceRegistry", "registry"]
