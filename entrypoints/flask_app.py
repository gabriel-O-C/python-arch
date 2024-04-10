
from datetime import datetime

from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import adapters.orm as orm
import config
from adapters.repository import SqlAlchemyRepository
from domain.model import OutOfStock
from service_layer.services import InvalidSku, allocate
from service_layer.services import add_batch as service_add_batch

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    session = get_session()
    repo = SqlAlchemyRepository(session)

    orderid = str(request.json["orderid"])
    sku = str(request.json["sku"])
    qty = int(request.json["qty"])

    try:
        batchref = allocate(orderid, sku, qty, repo, session)
    except (OutOfStock, InvalidSku) as e:
        return jsonify({"message": str(e)}), 400

    session.commit()

    return jsonify({"batchref": batchref}), 201

@app.route("/add_batch", methods=["POST"])
def add_batch():
    session = get_session()
    repo = SqlAlchemyRepository(session)

    eta = request.json["eta"]

    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    
    service_add_batch(request.json['ref'], request.json['sku'], request.json['qty'], eta, repo, session)


    return 'OK', 201