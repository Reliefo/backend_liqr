# flask_web/app.py
from backend.mongo.query import *
from flask import Flask, jsonify, request, send_from_directory, url_for
from flask_cors import CORS, cross_origin
import numpy as np
from flask_socketio import SocketIO, emit
import pickle
from backend.mongo.utils import return_restaurant

app = Flask(__name__)
# CORS(app, resources={r"/api/*":{"origins":"*"}})
# socketio = SocketIO(app,cors_allowed_origins="*")
socketio = SocketIO(app)


@socketio.on('connect', namespace='/adhara')
def connect():
    print('connected')
    emit('connect', {'data': 'Connected with me, sock'})


@socketio.on('disconnect', namespace='/adhara')
def disconnect():
    print("Disconnected :(")
    emit('response', {'data': 'Disconnected with me, sock'})


@socketio.on('fetchme', namespace='/adhara')
def fetch_all(message):
    print("IT's WORKING")
    print(message)
    emit('fetch', {'msg': "HERE IT IS TABLE      " + str(np.random.randint(100))})


@socketio.on('neworder', namespace='/adhara')
def send_new_orders(message):
    print("IT's WORKING")
    print(message)
    emit('fetch', {'msg': "HERE IT IS TABLE IT "})


@app.route('/')
def hello_world():
    return 'Hey, we have Flask in a Docker container! To fetch the menu go to /menu and to place an order go to /order'


@app.route('/menu')
def fetch_menu():
    str_menu = pickle.load(open('jason.pkl', 'rb'))
    return jsonify(str_menu)


@app.route('/rest')
def fetch_restaurant():
    str_menu = return_restaurant()
    return jsonify(str_menu)


@app.route('/order', methods=['POST'])
def receive_order():
    input_order = request.json
    if order_placement(input_order):
        return jsonify({'status': "Fuck yeah buddy, order placed"})
    else:
        return jsonify({'status': "Error, couldn't place the order"})


@app.route('/fetch_orders', methods=['POST'])
def fetch_orders():
    return fetch_order(np.random.randint(6))


@app.route('/send_orders', methods=['POST'])
def fetch_orders2():
    # new_order = fetch_order(np.random.randint(len(TableOrder.objects)))
    new_order = order_placement(generate_order())
    socketio.emit('new_orders', new_order, namespace='/adhara')
    # socketio.emit('fetch',{'hey':'asdfsdf'},namespace='/adhara')
    print("Sending")
    return new_order


@app.route('/send_cooking_updates', methods=['POST'])
def cooking_updates():

    # socketio.emit('fetch',{'hey':'asdfsdf'},namespace='/adhara')
    status_tuple = pick_order()

    order_status_cooking(status_tuple)

    sending_dict={}
    sending_dict['tableorder_id']=status_tuple[0]
    sending_dict['type']='cooking'
    sending_dict['order_id']=status_tuple[1]
    sending_dict['food_id']=status_tuple[2]
    sending_json=json_util.dumps(sending_dict)
    socketio.emit('order_updates', sending_json, namespace='/adhara')

    return sending_json

@app.route('/send_completed_updates', methods=['POST'])
def completed_updates():

    # socketio.emit('fetch',{'hey':'asdfsdf'},namespace='/adhara')
    status_tuple = pick_order2()

    order_status_completed(status_tuple)

    sending_dict={}
    sending_dict['tableorder_id']=status_tuple[0]
    sending_dict['type']='completed'
    sending_dict['order_id']=status_tuple[1]
    sending_dict['food_id']=status_tuple[2]
    sending_json=json_util.dumps(sending_dict)
    socketio.emit('order_updates', sending_json, namespace='/adhara')

    return sending_json


@app.route('/assist', methods=['POST'])
def assist_them():
    assistance_ob = assistance_req(generate_asstype())
    socketio.emit('assist', assistance_ob.to_json(), namespace='/adhara')
    server_name=send_assistance_req(str(assistance_ob.id))
    time.sleep(1)

    socketio.emit('assist_updates', {'assistance_id': str(assistance_ob.id),'server_name':server_name},namespace='/adhara')
    return str(assistance_ob.to_json())+' '+server_name


@app.route('/end_orders', methods=['POST'])
def fetch_orders3():
    print("YEAH IT; WORSFANDKLF")
    return jsonify("FUCK YESAH BUDY")


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5050)
