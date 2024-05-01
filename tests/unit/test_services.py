from typing import List

import pytest

import service_layer.services as services
from adapters import repository
from domain.model import Batch
from service_layer.unit_of_work import AbstractUnitOfWork


class FakeSession:
    commited = False

    def commit(self):
        self.commited = True


class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches: List[Batch]) -> None:
        self._batches = set(batches)

    def add(self, batch: Batch):
        self._batches.add(batch)

    def get(self, reference) -> Batch:
        return next(b for b in self._batches if b.reference == reference)

    def list(self) -> List[Batch]:
        return list(self._batches)


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.batches = FakeRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


def test_add_batch():
    uow = FakeUnitOfWork()

    services.add_batch("b1", "CRUNCY-ARMCHAIR", 100, None, uow)

    assert uow.batches.get("b1") is not None
    assert uow.committed


def test_allocate_returns_allocation():
    uow = FakeUnitOfWork()
    services.add_batch("batch1", "COMPLICATED-LAMP", 100, None, uow)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, uow)
    assert result == "batch1"


def test_allocate_errors_for_invalid_sku():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "AREALSKU", 100, None, uow)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, uow)


def test_commits():
    uow = FakeUnitOfWork()

    services.add_batch("b1", "COMPLICATED-LAMP", 100, None, uow)
    services.allocate("o1", "COMPLICATED-LAMP", 10, uow)

    assert uow.committed is True
