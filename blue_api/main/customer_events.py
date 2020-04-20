from .. import socket_io, our_namespace
from backend.mongo.query import *
from flask_socketio import emit


@socket_io.on('fetch_rest_customer', namespace=our_namespace)
def fetch_rest_customer(message):
    emit('restaurant_object', return_restaurant_customer(message))
    emit('home_screen_lists', home_screen_lists(message))


@socket_io.on('place_order', namespace=our_namespace)
def place_order(message):
    input_order = json_util.loads(message)
    socket_io.emit('fetch', message, namespace=our_namespace)
    print(input_order)
    new_order = order_placement(input_order)
    emit('new_orders', new_order)


"""
@socket_io.on('kitchen_updates', namespace=our_namespace)
socket_io.emit('order_updates')
"""
