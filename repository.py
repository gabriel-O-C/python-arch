from abc import ABC, abstractmethod
from typing import List

from model import Batch


class AbstractRepository(ABC):
    @abstractmethod
    def add(self, batch: Batch):
        raise NotImplementedError

    @abstractmethod
    def get(self, reference) -> Batch:
        raise NotImplementedError

class FakeRepository(AbstractRepository):
    def __init__(self, batches: List[Batch]) -> None:
        self._batches = set(batches)
    
    def add(self, batch: Batch):
        self._batches.add(batch)
    
    def get(self, reference) -> Batch:
        return next(b for b in self._batches if b.reference == reference)
    
    def list(self) -> List[Batch]:
        return list(self._batches)