import json
import logging
import os
import boto3
from flask import Flask, jsonify, request

app = Flask(__name__)  # create a Flask app
app.config['AWS_ACCESS_KEY_ID'] = os.environ['AWS_ACCESS_KEY_ID']  # set AWS access key
app.config['AWS_SECRET_ACCESS_KEY'] = os.environ['AWS_SECRET_ACCESS_KEY']  # set AWS secret access key
app.config['AWS_REGION'] = os.environ['AWS_REGION']  # set AWS region
app.config['S3_BUCKET'] = os.environ['S3_BUCKET']  # set S3 bucket name

logger = logging.getLogger()  # get root logger
logger.setLevel(logging.INFO)  # set log level to INFO


# Home route
@app.route('/', methods=['GET'])
def home():
    if request.method == 'GET':
        return jsonify(status=200, message='Hello, World!')
    return method_not_allowed()


# Route to handle POST requests
@app.route('/webhook', methods=['POST'])
def webhook():  # put application's code here
    if request.method == 'POST':  # only allow POST requests
        return process_txn(json.loads(request.data))  # upload txn JSON to S3 and return response
    return method_not_allowed()  # return error if method is not POST


def method_not_allowed():
    return jsonify(status=405, message='Method Not Allowed')  # return error if method is not POST


# Process request data
def process_txn(data):
    return put_object(create_s3_client(), data, get_txn_id(data))  # write to S3 and return response


# Write data to S3
def put_object(s3_client, data, txnid):
    try:
        upload_file(s3_client, json.dumps(data), txnid)  # write data to S3
    except Exception as e:  # catch exception if write fails
        return catch_error(e)  # log and return error
    return catch_success()  # return success response


# Create S3 client
def create_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],  # get AWS access key
        aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],  # get AWS secret access key
        region_name=app.config['AWS_REGION'],  # get AWS region
    )  # return S3 client


# Get txn ID
def get_txn_id(data):
    return data[0]['transaction']['signatures'][0]  # get transaction ID from request


# Upload file to S3
def upload_file(s3_client, data, txnid):
    s3_client.put_object(  # write data to S3
        Bucket=app.config['S3_BUCKET'],  # get bucket name
        Body=data,  # get data
        Key=f'{txnid}.json'  # set path
    )


# Catch error
def catch_error(e: Exception):
    logger.error(e)  # log error
    return jsonify(status=500, message='Failed to write data to S3')  # return error response


# Catch success
def catch_success():
    logger.info('Data written to S3')  # log success
    return jsonify(status=200, message='Data written to S3')  # return success response


if __name__ == '__main__':  # only run if script is executed directly
    app.run()  # run the Flask app
