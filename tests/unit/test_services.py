from typing import List

import pytest

from src.allocation.adapters import repository
from src.allocation.domain import model
from src.allocation.service_layer import services
from src.allocation.service_layer.unit_of_work import AbstractUnitOfWork


class FakeSession:
    commited = False

    def commit(self):
        self.commited = True


class FakeRepository(repository.AbstractProductRepository):
    def __init__(self, products: List[model.Product]) -> None:
        self._products = set(products)

    def add(self, product):
        self._products.add(product)

    def get(self, sku) -> model.Product:
        return next((p for p in self._products if p.sku == sku), None)

    def list(self) -> List[model.Product]:
        return list(self._products)


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.products = FakeRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


def test_add_batch():
    uow = FakeUnitOfWork()

    services.add_batch("b1", "CRUNCY-ARMCHAIR", 100, None, uow)

    assert uow.products.get("CRUNCY-ARMCHAIR") is not None
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
