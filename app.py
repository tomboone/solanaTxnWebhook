"""
Module to handle POST requests and write transaction data to a MongoDB database
"""
import json
import os
import urllib.parse
from flask import Flask, jsonify, request
from pymongo import MongoClient
app = Flask(__name__)  # create a Flask app

TLS = ''
if os.getenv('MONGO_TLS') == 'True':  # check if TLS is enabled
    TLS = 'tls=true'
user = os.getenv('MONGO_USER')  # get username from environment variable
pwd = urllib.parse.quote_plus(os.getenv('MONGO_PWD'))  # get password from environment variable
uri = (f'mongodb://{user}:{pwd}@{os.getenv("MONGO_HOST")}:'  # create a MongoDB URI
       f'{os.getenv("MONGO_PORT")}/?authSource={os.getenv("MONGO_DB")}&{TLS}')
client = MongoClient(uri)  # create a MongoDB client
db = client[os.getenv('MONGO_DB')]  # get a database
collection = db[os.getenv('MONGO_COLLECTION')]  # get a collection


@app.route('/', methods=['GET'])
def home():
    """
    Home route
    """
    return jsonify(status=200, message='Hello, World!')


@app.route('/webhook', methods=['POST'])
def webhook():  # put application's code here
    """
    Webhook route
    """
    if 'Authorization' in request.headers:  # check if X-Auth-Key header is present
        if request.headers.get('Authorization') == os.getenv('AUTH_KEY'):
            return process_txn(json.loads(request.data))  # process txn data if X-Auth-Key present
    return catch_unauthorized()  # return unauthorized response if X-Auth-Key is not present


def process_txn(data):
    """
    Process request data
    """
    result = collection.insert_one({  # insert txn data to db
        '_id': data[0]['transaction']['signatures'][0],  # get txn ID
        'timestamp': data[0]['blockTime'],  # get block time
        'txn': data[0]  # get transaction data
    })
    if result.acknowledged:  # check if txn data is written to db
        return catch_success()  # return success response
    return catch_error()  # return error response


def catch_error():
    """
    Catch error
    """
    return jsonify(status=500, message='Internal server error')  # return error response


def catch_success():
    """
    Catch success
    """
    return jsonify(status=200, message='Txn data written to database')  # return success response


def catch_unauthorized():
    """
    Catch unauthorized
    """
    return jsonify(status=401, message='Unauthorized')  # return unauthorized response


if __name__ == '__main__':
    app.run()
