from .. import socket_io, our_namespace
from backend.mongo.query import *


@socket_io.on('place_order', namespace=our_namespace)
def place_order(message):
    input_order = json_util.loads(message)
    new_order = order_placement(input_order)
    socket_io.emit('new_orders', new_order, namespace=our_namespace)

