from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/button1')
def handle_button1():
    mssg = "Manchester: Request for /button1 recieved. Sending request to localhost:5000"
    resp = requests.get('http://localhost:5000/secrets')
    print(resp)
    print(resp.content)
    mssg += "\n" +resp.text
    return jsonify(message=resp.text)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0" ,port=5001)