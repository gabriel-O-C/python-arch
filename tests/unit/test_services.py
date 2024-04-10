import pytest

import domain.model as model
import service_layer.services as services


class FakeSession:
    commited = False

    def commit(self):
        self.commited = True


class FakeRepository(set):
    @staticmethod
    def for_batch(ref, sku, qty, eta=None):
        return FakeRepository([model.Batch(ref, sku, qty, eta)])

    def list(self):
        return list(self)

def test_commits():
    repo =  FakeRepository.for_batch("b1", "COMPLICATED-LAMP", 100, None)

    session = FakeSession()

    services.allocate("o1", "COMPLICATED-LAMP", 10, repo, session)

    assert session.commited is True


def test_returns_allocations():
    repo =  FakeRepository.for_batch('batch1', 'COMPLICATED-LAMP', 10, eta=None)

    result = services.allocate("o1", "COMPLICATED-LAMP", 10, repo, FakeSession())

    assert result == "batch1"


def test_error_for_invalid_sku():
    repo = FakeRepository.for_batch("b1", "COMPLICATED-LAMP", 100, None)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENT-LAMP"):
        services.allocate("o1", "NONEXISTENT-LAMP", 10, repo, FakeSession())
