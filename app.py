import json
import logging
import os

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Txn(db.Model):
    __tablename__ = 'txn'
    id: Mapped[str] = mapped_column(primary_key=True)
    blocktime: Mapped[int] = mapped_column(nullable=False)
    data: Mapped[str] = mapped_column(unique=True, nullable=False)

    def __init__(self, txn_id, blocktime, data):
        self.id = txn_id
        self.blocktime = blocktime
        self.data = data

    def __repr__(self):
        return f'<Txn {self.id}>'


app = Flask(__name__)  # create a Flask app

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB')  # set database URI
db.init_app(app)  # initialize database
with app.app_context():
    db.create_all()  # create database tables

logger = logging.getLogger()  # get root logger
logger.setLevel(logging.INFO)  # set log level to INFO


# Home route
@app.route('/', methods=['GET'])
def home():
    return jsonify(status=200, message='Hello, World!')


# Route to handle POST requests
@app.route('/webhook', methods=['POST'])
def webhook():  # put application's code here
    return process_txn(json.loads(request.data))  # write txn to db


# Process request data
def process_txn(data):
    if data[0]['meta']['err'] is None:  # check if txn is successful
        try:  # try to log txn to db
            txn = Txn(  # create Txn object
                txn_id=get_txn_id(data),
                blocktime=get_txn_blocktime(data),
                data=json.dumps(data[0])
            )
            db.session.add(txn)  # add txn to session
            db.session.commit()  # commit txn to db
        except Exception as e:  # catch error
            return catch_error(e)  # return error response
        return catch_success()  # return success response if txn is logged
    else:
        return catch_failed()  # return null for failed txn


# Get txn ID
def get_txn_id(data):
    return data[0]['transaction']['signatures'][0]  # get transaction ID from request


# Get txn blocktime
def get_txn_blocktime(data):
    return data[0]['blockTime']  # get block time from request


# Catch error
def catch_error(e):
    logger.error(e)  # log error
    return jsonify(status=500, message='Error writing data to database')  # return error response


# Catch failed
def catch_failed():
    return jsonify(status=200, message='Failed txn: no data logged')  # return failure response


# Catch success
def catch_success():
    logger.info('Data written to S3')  # log success
    return jsonify(status=200, message='Txn data written to database')  # return success response


if __name__ == '__main__':
    app.run()
