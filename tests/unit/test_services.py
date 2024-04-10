from typing import List

import pytest

import service_layer.services as services
from adapters import repository
from domain.model import Batch


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


def test_add_batch():
    repo, session = FakeRepository([]), FakeSession()

    services.add_batch("b1", "CRUNCY-ARMCHAIR", 100, None, repo, session)

    assert repo.get("b1") is not None
    assert session.commited


def test_allocate_returns_allocation():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("batch1", "COMPLICATED-LAMP", 100, None, repo, session)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, repo, session)
    assert result == "batch1"


def test_allocate_errors_for_invalid_sku():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "AREALSKU", 100, None, repo, session)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, repo, FakeSession())


def test_commits():
    repo, session = FakeRepository([]), FakeSession()

    services.add_batch("b1", "COMPLICATED-LAMP", 100, None, repo, session)
    services.allocate("o1", "COMPLICATED-LAMP", 10, repo, session)

    assert session.commited is True
