from abc import ABC, abstractmethod
from typing import List

from ..models import SearchResult


class BaseSearcher(ABC):
    name: str

    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        pass
