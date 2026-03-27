from abc import ABC, abstractmethod
from app.schemas import SearchResult

class BaseSearchEngine(ABC):
    name: str = "base"

    @abstractmethod
    def search(self, query: str, page: int = 1, per_page: int = 10) -> list[SearchResult]:
        pass
