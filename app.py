# flask_web/app.py

from flask import Flask,jsonify, request, send_from_directory, url_for
app = Flask(__name__)
import pickle
from backend.mongo.utils import return_restaurant

@app.route('/')
def hello_world():
    return 'Hey, we have Flask in a Docker container! To fetch the menu go to /menu and to place an order go to /order'

@app.route('/menu')
def fetch_menu():
    str_menu = pickle.load(open('jason.pkl','rb'))
    return jsonify(str_menu)

@app.route('/rest')
def fetch_restaurant():
    str_menu=return_restaurant()
    return jsonify(str_menu)

@app.route('/order', methods=['POST'])
def receive_order():
    print(request)
    content = request.json
    print(content)
    return jsonify({'status':"Fuck yeah buddy, order placed",'return': str(content)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port="5050")

