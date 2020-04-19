# flask_web/app.py
import traceback
# import eventlet
from werkzeug.security import check_password_hash, generate_password_hash
import functools
from backend.mongo.mongo_setup import *
from flask import Flask, jsonify, request, send_from_directory, url_for
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required, logout_user
from flask_cors import CORS, cross_origin
import numpy as np
from flask_socketio import SocketIO, emit, disconnect, join_room
import pickle
from backend.mongo.utils import return_restaurant
import threading
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, jwt_refresh_token_required, create_refresh_token, get_jwt_identity,
    verify_jwt_in_request,
    fresh_jwt_required
)

app = Flask(__name__)
CORS(app)
# app.config['CORS_HEADERS']="Content-Type"
app.config["SECRET_KEY"] = "reliefoasbvuierjvnsdv23"
our_namespace = '/reliefo'
app.config['JWT_TOKEN_LOCATION'] = ['query_string', 'headers']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 15000
app.config['JWT_SECRET_KEY'] = 'vniodnv4o2949fjerf'  # Change this!
app.config['PROPAGATE_EXCEPTIONS'] = True
login_manager = LoginManager(app)

jwt = JWTManager(app)
# CORS(app, resources={r"/api/*":{"origins":"*"}})
# socket_io = SocketIO(app,cors_allowed_origins="*")
socket_io = SocketIO(app, logger=True, engineio_logger=False, ping_timeout=10, ping_interval=5,
                     cors_allowed_origins="*")
all_clients = []
active_clients = []


# eventlet.monkey_patch()


class AppUser(UserMixin, Document):
    username = StringField(max_length=30)
    password = StringField()
    sid = StringField()
    room = StringField()


@login_manager.user_loader
def load_user(user_id):
    return AppUser.objects.get(id=user_id)


# @jwt.expired_token_loader
# def my_expired_token_callback(expired_token):
#     token_type = expired_token['type']
#     return jsonify({
#         'status': 401,
#         'sub_status': 42,
#         'msg': 'The {} token has expired'.format(token_type)
#     }), 401


@login_manager.request_loader
def load_user_from_request(request):
    # first, try to login using the api_key url arg
    api_key = request.args.get('user_key')
    if api_key:
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user
    # finally, return None if both methods did not login the user
    return None


@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_username = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=current_username),
        'code': '200'
    }
    return jsonify(ret)


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)

    return wrapped


@app.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return json_util.dumps({"status": "You're logged in ", "code": "202"})
    if request.method == 'POST':
        check_user = AppUser.objects(username=request.form["username"]).first()
        if check_user:
            if check_password_hash(check_user['password'], request.form["password"]):
                login_user(check_user)
                access_token = create_access_token(identity=request.form["username"])
                refresh_token = create_refresh_token(identity=request.form["username"])
                return json_util.dumps(
                    {"status": "Login Success", "jwt": access_token, "refresh_token": refresh_token, "code": "200"})
    return json_util.dumps({"status": "Authentication Failed", "code": "401"})


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if AppUser.objects.filter(username=request.form["username"]):
            return json_util.dumps({"status": "Already Registered"})
        hashpass = generate_password_hash(request.form["password"], method='sha256')
        assigned_room = "kids_room" if request.form["username"][:3] == "KID" else "adults_room"
        print(request.form["username"], " joined ", assigned_room)
        hey = AppUser(username=request.form["username"], password=hashpass, room=assigned_room).save()
        login_user(hey)
        return json_util.dumps({"status": "Registration successful"})
    return json_util.dumps({"status": "Registration failed"})


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return "Logout Successful"


@socket_io.on('connect', namespace=our_namespace)
# @fresh_jwt_required
@jwt_required
def connect():
    print('connected')
    print(request.args)
    username = get_jwt_identity()
    print(username)
    previous_sid = AppUser.objects(username=username).first().sid
    # if False:
    if previous_sid:
        print("I have it here", previous_sid)
        disconnect(previous_sid)
    AppUser.objects(username=username).first().update(set__sid=request.sid)
    # if AppUser.objects(username=username).first().room == "kids_room":
    #     join_room("kids_room")
    # else:
    #     join_room("adults_room")
    all_clients.append(request.sid)
    # if current_user.is_authenticated:
    if False:
        emit('fetch',
             {'message': '{-1} has joined'.format(current_user.name)},
             broadcast=True)
    # disconnect(request.sid)


@socket_io.on('shake_hands', namespace=our_namespace)
def shake_hands(message):
    print(message)


@socket_io.on('disconnect', namespace=our_namespace)
def on_disconnect():
    print("Disconnected :( from ", request.sid)


@socket_io.on('rest_with_id', namespace=our_namespace)
def fetch_rest_object(message):
    rest_json = return_restaurant(message)
    emit('restaurant_object', rest_json)
    return rest_json


@socket_io.on('place_order', namespace=our_namespace)
def place_order(message):
    input_order = json_util.loads(message)
    new_order = order_placement(input_order)
    socket_io.emit('new_orders', new_order, namespace=our_namespace)


@socket_io.on('configuring_restaurant', namespace=our_namespace)
def configuring_restaurant_event(message):
    print("IT's WORKING")
    output = configuring_restaurant(json_util.loads(message))
    print(message)
    emit('updating_config', json_util.dumps(output))


@socket_io.on('fetchme', namespace=our_namespace)
def fetch_all(message):
    print("here i am printingi requiest id", request.sid, request.namespace, str(current_user.is_authenticated))
    print(all_clients)
    # global active_clients
    # socket_io.emit('hand_shake', active_clients, namespace=our_namespace)
    # active_clients = []
    # thr = threading.Thread(target=hand_shake_check, args=(), kwargs={})
    # thr.start()  # Will run "foo"
    # print(threading.active_count())
    print(message)
    print(datetime.datetime.now())
    emit('fetch', {'msg': "HERE IT IS TABLE      " + str(np.random.randint(100))}, )


@socket_io.on('fetch_handshake', namespace=our_namespace)
def hand_shake_fetch(message):
    print("here i am printingi requiest id", request.sid, request.namespace, str(current_user.is_authenticated))
    print(all_clients)
    global active_clients
    socket_io.emit('hand_shake', active_clients, namespace=our_namespace)
    active_clients = []
    thr = threading.Thread(target=hand_shake_check, args=(), kwargs={})
    thr.start()  # Will run "foo"
    print(threading.active_count())
    print(message)
    print(datetime.datetime.now())
    emit('fetch', {'msg': "HERE IT IS TABLE      " + str(np.random.randint(100))}, )


@socket_io.on('hand_shook', namespace=our_namespace)
def hand_shook(message):
    active_clients.append(request.sid)
    print("got ti back from ", request.sid)


def hand_shake_check():
    time.sleep(5)
    for client in all_clients:
        if client in active_clients:
            continue
        with app.test_request_context('/'):
            disconnect(client, namespace=our_namespace)
    return


@socket_io.on('fetch_order_lists', namespace=our_namespace)
def fetch_order_lists(message):
    try:
        lists_json = Restaurant.objects[0].fetch_order_lists()
    except NameError:
        try:
            emit('order_lists', str(traceback.format_exc()))
        except TypeError:
            emit('order_lists', 'Nothing is working')

    emit('order_lists', lists_json)


@socket_io.on('kitchen_updates', namespace=our_namespace)
def send_new_orders(message):
    status_tuple = (message['table_order_id'], message['order_id'], message['food_id'])
    if message['type'] == 'cooking':
        order_status_cooking(status_tuple)
    else:
        order_status_completed(status_tuple)

    sending_dict = {'table_order_id': status_tuple[0], 'type': message['type'], 'order_id': status_tuple[1],
                    'food_id': status_tuple[2], 'kitchen_app_id': message['kitchen_app_id']}
    sending_json = json_util.dumps(sending_dict)
    socket_io.emit('order_updates', sending_json, namespace=our_namespace)
    emit('fetch', {'msg': message})


@app.route('/')
def hello_world():
    return 'Hey, we have Flask in a Docker container! To fetch the menu go to /menu and to place an order go to /order'


@app.route('/menu')
def fetch_menu():
    print(verify_jwt_in_request(), 'asdfasdf')
    str_menu = pickle.load(open('jason.pkl', 'rb'))
    return jsonify(str_menu)


@app.route('/rest')
def fetch_restaurant():
    rest_json = return_restaurant("BNGHSR0001")
    # socket_io.emit('restaurant_object', rest_json, namespace=our_namespace)
    return rest_json


@app.route('/rest2')
def fetch_restaurant2():
    rest_json = return_restaurant("BNGHSR0002")
    # socket_io.emit('restaurant_object', rest_json, namespace=our_namespace)
    return rest_json


@app.route('/order', methods=['POST'])
def receive_order():
    input_order = request.json
    if order_placement(input_order):
        return jsonify({'status': "Hell yeah buddy, order placed"})
    else:
        return jsonify({'status': "Error, couldn't place the order"})


@app.route('/send_room_messages', methods=['POST'])
def disconnect_user():
    data = request.json
    socket_io.emit('order_lists', Restaurant.objects[0].fetch_order_lists(), room=data['room'], namespace=our_namespace)
    return request.json


@app.route('/send_orders', methods=['GET'])
def fetch_orders2():
    # new_order = fetch_order(np.random.randint(len(TableOrder.objects)))
    new_order = order_placement(generate_order())
    socket_io.emit('new_orders', new_order, namespace=our_namespace)
    # socket_io.emit('fetch',{'hey':'asdfsdf'},namespace=our_namespace)
    print("Sending")
    return new_order


@app.route('/send_cooking_updates', methods=['POST'])
def cooking_updates():
    # socket_io.emit('fetch',{'hey':'asdfsdf'},namespace=our_namespace)
    status_tuple = pick_order()

    order_status_cooking(status_tuple)

    sending_dict = {'table_order_id': status_tuple[0], 'type': 'cooking', 'order_id': status_tuple[1],
                    'food_id': status_tuple[2]}
    if len(status_tuple) == 4:
        sending_dict['food_options_id'] = status_tuple[3]
    sending_json = json_util.dumps(sending_dict)
    socket_io.emit('order_updates', sending_json, namespace=our_namespace)

    return sending_json


@app.route('/send_completed_updates', methods=['POST'])
def completed_updates():
    # socket_io.emit('fetch',{'hey':'asdfsdf'},namespace=our_namespace)
    status_tuple = pick_order2()

    order_status_completed(status_tuple)

    sending_dict = {'table_order_id': status_tuple[0], 'type': 'completed', 'order_id': status_tuple[1],
                    'food_id': status_tuple[2]}
    sending_json = json_util.dumps(sending_dict)
    socket_io.emit('order_updates', sending_json, namespace=our_namespace)

    return sending_json


@app.route('/assist', methods=['POST'])
def assist_them():
    assistance_ob = assistance_req(generate_asstype())
    socket_io.emit('assist', assistance_ob.to_json(), namespace=our_namespace)
    staff_name = send_assistance_req(str(assistance_ob.id))
    time.sleep(1)

    socket_io.emit('assist_updates', {'assistance_id': str(assistance_ob.id), 'staff_name': staff_name},
                   namespace=our_namespace)
    return str(assistance_ob.to_json()) + ' ' + staff_name


@app.route('/mongo_setup', methods=['GET'])
def mongo_setup():
    setup_mongo()
    return "All data has been pushed to mongo"


@app.route('/user_scan', methods=['POST'])
def user_scan_portal():
    content = request.json
    table_no = content['table']
    unique_id = content['unique_id']
    table_id = str(Table.objects[int(table_no)].id)
    user_id = str(user_scan(table_id, unique_id))
    socket_io.emit('user_scan', json_util.dumps({"table_no": table_no, "user_id": user_id, "table_id": table_id}),
                   namespace=our_namespace)
    return json_util.dumps({"table_no": table_no, "user_id": user_id, "table_id": table_id})


if __name__ == '__main__':
    socket_io.run(app, debug=True, host='0.0.0.0', port=5050)
