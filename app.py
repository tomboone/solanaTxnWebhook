import json
import os
import urllib.parse
from flask import Flask, jsonify, request
from pymongo import MongoClient
app = Flask(__name__)  # create a Flask app

tls = ''
if os.getenv('MONGO_TLS') == 'True':  # check if TLS is enabled
    tls = 'tls=true'
user = os.getenv('MONGO_USER')  # get username from environment variable
pwd = urllib.parse.quote_plus(os.getenv('MONGO_PWD'))  # get password from environment variable
uri = (f'mongodb://{user}:{pwd}@{os.getenv("MONGO_HOST")}:'
       f'{os.getenv("MONGO_PORT")}/?authSource={os.getenv("MONGO_DB")}&{tls}')  # create a MongoDB URI
client = MongoClient(uri)  # create a MongoDB client
db = client[os.getenv('MONGO_DB')]  # get a database
collection = db[os.getenv('MONGO_COLLECTION')]  # get a collection


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
    try:  # try to log txn to db
        collection.insert_one({  # insert txn data to db
            '_id': data[0]['transaction']['signatures'][0],  # get txn ID
            'timestamp': data[0]['blockTime'],  # get block time
            'txn': data[0]  # get transaction data
        })
    except Exception as e:  # catch error
        return catch_error(e)  # return error response
    return catch_success()  # return success response if txn is logged


# Catch error
def catch_error(e):
    return jsonify(status=500, message=e)  # return error response


# Catch success
def catch_success():
    return jsonify(status=200, message='Txn data written to database')  # return success response


if __name__ == '__main__':
    app.run()
