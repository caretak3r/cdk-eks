import logging
import boto3
from flask import json, jsonify

logger = logging.getLogger(__name__)

class SecretsManager:
    def __init__(self):
        self.client = boto3.client("secretsmanager", region_name="us-west-2")
    def get_secrets(self):
        try:
            response = self.client.list_secrets()
            secrets = []
            for secret in response["SecretList"]:
                secrets.append(secret["Name"])
            if secrets:
                logger.info("Secrets retrieved successfully.")
            else:
                logger.info("Zero secrets returned without error.")
            while "NextToken" in response:
                response = self.client.list_secrets(NextToken=response["NextToken"])
                for secret in response["SecretList"]:
                    secrets.append(secret["Name"])
                logger.info("Additional secrets retrieved successfully.")
            dict = {'SecretList': secrets, 'ResponseMetadata': response["ResponseMetadata"]}
            resp = jsonify(dict)
            return resp
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}.")
            raise
    def post_secrets(self, secret_name, secret_value):
        try:
            response = self.client.create_secret(Name=secret_name, SecretString=secret_value)
            logging.info("Secret created successfully.")
            return response
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}.")
            raise
    def get_secret(self, secret_name):
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            logging.info("Secret retrieved successfully.")
            dict = {'Name': response["Name"], 'SecretString': response["SecretString"], 'ResponseMetadata': response["ResponseMetadata"]}
            resp = jsonify(dict)
            return resp
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}.")
            raise
    def put_secret(self, secret_name, secret_value):
        try:
            response = self.client.put_secret_value(SecretId=secret_name, SecretString=secret_value)
            logging.info("Secret updated successfully.")
            return response
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}.")
            raise
    