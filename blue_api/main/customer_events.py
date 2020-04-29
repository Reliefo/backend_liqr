from .. import socket_io, our_namespace
from backend.mongo.query import *
from flask_socketio import emit
from backend.aws_api.sns_pub import push_assistance_request_notification


@socket_io.on('fetch_rest_customer', namespace=our_namespace)
def fetch_rest_customer(message):
    emit('restaurant_object', return_restaurant_customer(message))
    emit('home_screen_lists', home_screen_lists(message))


@socket_io.on('place_personal_order', namespace=our_namespace)
def place_personal_order(message):
    input_order = json_util.loads(message)
    socket_io.emit('fetch', message, namespace=our_namespace)
    new_order = order_placement(input_order)
    socket_io.emit('new_orders', new_order, namespace=our_namespace)


@socket_io.on('push_to_table_cart', namespace=our_namespace)
def push_to_table(message):
    input_order = json_util.loads(message)
    socket_io.emit('fetch', message, namespace=our_namespace)
    table_cart_order = push_to_table_cart(input_order)
    socket_io.emit('table_cart_orders', table_cart_order, namespace=our_namespace)


@socket_io.on('place_table_order', namespace=our_namespace)
def place_table_order(message):
    table_id_dict = json_util.loads(message)
    socket_io.emit('fetch', table_id_dict, namespace=our_namespace)
    table_id = table_id_dict['table_id']
    socket_io.emit('fetch', message, namespace=our_namespace)
    new_order = order_placement_table(table_id)
    socket_io.emit('new_orders', new_order, namespace=our_namespace)


"""
@socket_io.on('kitchen_updates', namespace=our_namespace)
socket_io.emit('order_updates')
"""


@socket_io.on('assistance_requests', namespace=our_namespace)
def assistance_requests(message):
    input_dict = json_util.loads(message)
    assistance_ob = assistance_req(input_dict)
    returning_message = assistance_ob.to_json()
    returning_dict = json_util.loads(returning_message)
    user_id = str(returning_dict.pop('user'))
    assistance_req_id = str(returning_dict.pop('_id'))
    returning_dict['user_id'] = user_id
    returning_dict['assistance_req_id'] = assistance_req_id
    push_assistance_request_notification(returning_dict)
    returning_dict['msg'] = "Service has been requested"
    socket_io.emit('assist', json_util.dumps(returning_dict), namespace=our_namespace)
