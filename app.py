from flask_sockets import Sockets
from flask import Flask,jsonify, request, send_from_directory, url_for
from backend.mongo.query import order_placement,fetch_order
from backend.mongo.utils import return_restaurant

import pickle

app = Flask(__name__)
sockets = Sockets(app)




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


@sockets.route('/echo')
def echo_socket(ws):
    while not ws.closed:
        message = ws.receive()
        print(message)
        with open('fuck.txt','w') as f:
            f.write(message)
        ws.send(message+'Mello')


@sockets.route('/connect')
def connect(ws):
    print('connected')
    ws.send({'data':'Connected with me, sock'})

# @socketio.on('disconnect', namespace='/')
# def disconnect():
#     emit('response', {'data':'Disconnected with me, sock'})

@sockets.route('/fetchme')
def fetch_all(ws):
    msg=ws.receive()
    print("IT's WORKING")
    ws.send({'msg':"HERE IT IS TABLE IT ",'ori':msg})

if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('0.0.0.0', 5050), app, handler_class=WebSocketHandler)
    server.serve_forever()
