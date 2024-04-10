import domain.model as model
from adapters.repository import AbstractRepository


class InvalidSku(Exception):
  pass


def is_valid_sku(sku, batches):
  return sku in {b.sku for b in batches}


def allocate(orderid: str, sku: str, qty: int, repo: AbstractRepository, session) -> str:
  batches = repo.list()

  line = model.OrderLine(orderid, sku, qty)
  if not is_valid_sku(sku, batches):
    raise InvalidSku(f'Invalid sku {sku}')
  

  batchref = model.allocate(line, batches)
  session.commit()
  return batchref