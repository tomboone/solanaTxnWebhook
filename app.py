import json
import logging
import os

from flask import Flask, jsonify, request
from pymongo import MongoClient
app = Flask(__name__)  # create a Flask app

client = MongoClient(os.getenv('MONGO_URI'))  # create a MongoDB client
db = client[os.getenv('MONGO_DB')]  # get a database
collection = db[os.getenv('MONGO_COLLECTION')]  # get a collection

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
            collection.insert_one({  # insert txn data to db
                '_id': get_txn_id(data),  # get txn ID
                'txn': data[0]['transaction']  # get transaction data
            })
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
