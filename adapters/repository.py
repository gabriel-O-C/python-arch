from abc import ABC, abstractmethod

from domain.model import Product


class AbstractProductRepository(ABC):
    @abstractmethod
    def add(self, product: Product):
        raise NotImplementedError

    @abstractmethod
    def get(self, sku) -> Product:
        raise NotImplementedError
    
    @abstractmethod
    def list(self):
        raise NotImplementedError


class SqlAlchemyRepository(AbstractProductRepository):
    def __init__(self, session):
        self.session = session

    def add(self, product: Product):
        self.session.add(product)

    def get(self, sku):
        return self.session.query(Product).filter_by(sku=sku).first()

    def list(self):
        return self.session.query(Product).all()
