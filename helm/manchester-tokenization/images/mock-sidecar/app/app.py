from flask import Flask, request

from api import SecretsManager

app = Flask(__name__)

# secret
secrets_env = SecretsManager()

@app.route('/secrets', methods=['GET'])
def get_secrets():
    return secrets_env.get_secrets()

@app.route('/secrets', methods=['POST'])
def post_secrets():
    data = request.json
    secret_name = data.get("secret_name", None)
    secret_value = data.get("secret_value", None)
    if secret_name is None or secret_value is None:
        return
    return secrets_env.post_secrets(secret_name, secret_value)

@app.route('/secrets/<secret_name>', methods=['GET'])
def get_secret(secret_name):
    return secrets_env.get_secret(secret_name)

@app.route('/secrets', methods=['PUT'])
def put_secret():
    data = request.json
    secret_name = data.get("secret_name", None)
    secret_value = data.get("secret_value", None)
    if secret_name is None or secret_value is None:
        return
    return secrets_env.put_secret(secret_name, secret_value)



if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=5000)
