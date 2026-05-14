"""
Abstract base class for geographic data source plugins.
"""
from abc import ABC, abstractmethod
from typing import List
from ..models import QueryParams, SearchResult, DownloadResult, DataSourceMeta


class GeoDataSource(ABC):
    """All geographic data source plugins must implement this interface."""

    @abstractmethod
    def can_handle(self, query: QueryParams) -> bool:
        """Return True if this source can serve this query."""
        ...

    @abstractmethod
    def search(self, query: QueryParams) -> List[SearchResult]:
        """Find matching datasets. Returns list of SearchResult."""
        ...

    @abstractmethod
    def download(self, result: SearchResult, output_path: str) -> DownloadResult:
        """Download a specific dataset to output_path."""
        ...

    @abstractmethod
    def get_metadata(self) -> DataSourceMeta:
        """Return metadata about this data source."""
        ...
