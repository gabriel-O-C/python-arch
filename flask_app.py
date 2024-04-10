from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
import orm
from model import OrderLine, OutOfStock
from repository import SqlAlchemyRepository
from services import InvalidSku, allocate

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    session = get_session()
    repo = SqlAlchemyRepository(session)

    line = OrderLine(
        str(request.json["orderid"]), str(request.json["sku"]), str(request.json["qty"])
    )
    try:
        batchref = allocate(line, repo, session)
    except (OutOfStock, InvalidSku) as e:
        return jsonify({"message": str(e)}), 400

    session.commit()

    return jsonify({"batchref": batchref}), 201
