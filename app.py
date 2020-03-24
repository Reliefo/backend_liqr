# flask_web/app.py
from backend.mongo.query import order_placement,fetch_order
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

    input_order = request.json
    if(order_placement(input_order)):
        return jsonify({'status':"Fuck yeah buddy, order placed"})
    else:
        return jsonify({'status':"Error, couldn't place the order"})


@app.route('/fetch_orders', methods=['POST'])
def fetch_orders():
    return fetch_order()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port="5050")
