import pytest

import adapters.repository as repository
import domain.model as model
import service_layer.services as services


class FakeSession():
  commited = False

  def commit(self):
    self.commited = True



def test_commits():
  line = model.OrderLine('o1', 'COMPLICATED-LAMP', 10)

  batch = model.Batch('b1', 'COMPLICATED-LAMP', 100, None)

  repo =  repository.FakeRepository([batch])

  session = FakeSession()


  services.allocate(line, repo, session)

  assert session.commited is True

def test_returns_allocations():

  line = model.OrderLine('o1', 'COMPLICATED-LAMP', 10)

  batch = model.Batch('b1', 'COMPLICATED-LAMP', 100, None)

  repo =  repository.FakeRepository([batch])

  result = services.allocate(line, repo, FakeSession())


  assert result == 'b1'



def test_error_for_invalid_sku():
  line = model.OrderLine('o1', 'NONEXISTENT-LAMP', 10)

  batch = model.Batch('b1', 'COMPLICATED-LAMP', 100, None)

  repo =  repository.FakeRepository([batch])

  with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENT-LAMP"):
    services.allocate(line, repo, FakeSession())