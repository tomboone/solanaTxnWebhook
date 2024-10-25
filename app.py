import json
import logging

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Txn(db.Model):
    __tablename__ = 'txn'
    id: Mapped[str] = mapped_column(primary_key=True)
    txn_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    blocktime: Mapped[int] = mapped_column(nullable=False)
    data: Mapped[str] = mapped_column(unique=True, nullable=False)

    def __init__(self, txn_id, blocktime, data):
        self.id = txn_id
        self.blocktime = blocktime
        self.data = data

    def __repr__(self):
        return f'<Txn {self.txn_id}>'


app = Flask(__name__)  # create a Flask app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///txn.db'  # set database URI
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
    outcome = process_txn(json.loads(request.data))  # upload txn JSON to S3 and return response
    if isinstance(outcome, Exception):
        return catch_error(outcome)
    return catch_success()


# Process request data
def process_txn(data):
    try:
        Txn(  # create Txn object
            txn_id=get_txn_id(data),
            blocktime=get_txn_blocktime(data),
            data=json.dumps(data[0])
        )
    except Exception as e:  # catch error
        return e  # return error response
    return data  # return success response


# Get txn ID
def get_txn_id(data):
    return data[0]['transaction']['signatures'][0]  # get transaction ID from request


# Get txn blocktime
def get_txn_blocktime(data):
    return data[0]['blockTime']  # get block time from request


# Catch error
def catch_error(e):
    logger.error(e)  # log error
    return jsonify(status=500, message='Failed to write data to S3')  # return error response


# Catch success
def catch_success():
    logger.info('Data written to S3')  # log success
    return jsonify(status=200, message='Data written to S3')  # return success response


if __name__ == '__main__':
    app.run()
