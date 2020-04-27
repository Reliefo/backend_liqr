from .. import socket_io, our_namespace
from backend.mongo.query import *
from flask_socketio import emit


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
    input_request = json_util.loads(message)
    assistance_ob = assistance_req(input_request)
    socket_io.emit('assist', assistance_ob.to_json(), namespace=our_namespace)
