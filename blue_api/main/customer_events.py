from .. import socket_io, our_namespace
from backend.mongo.query import *
from flask_socketio import emit
from backend.aws_api.sns_pub import push_assistance_request_notification


@socket_io.on('fetch_rest_customer', namespace=our_namespace)
def fetch_rest_customer(message):
    socket_io.emit('fetch', message, namespace=our_namespace)
    user_rest_dets = json_util.loads(message)
    user_id = user_rest_dets['user_id']
    rest_id = user_rest_dets['restaurant_id']
    emit('user_details', return_user_details(user_id))
    emit('table_details', return_table_details(user_id))
    #TODO Remove this after frontend integraton
    emit('restaurant_object', return_restaurant_customer(rest_id))
    emit('home_screen_lists', home_screen_lists(rest_id))


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
    push_to_table_cart(input_order)
    table_cart_order = Table.objects.get(id=input_order['table']).table_cart.to_json()
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
    socket_io.emit('fetch', message, namespace=our_namespace)
    assistance_ob = assistance_req(input_dict)
    returning_message = assistance_ob.to_json()

    returning_dict = json_util.loads(returning_message)
    user_id = str(returning_dict.pop('user'))
    assistance_req_id = str(returning_dict.pop('_id'))
    user_obj = User.objects.get(id=user_id)
    returning_dict['user_id'] = user_id
    returning_dict['user'] = user_obj.name
    returning_dict['assistance_req_id'] = assistance_req_id
    returning_dict['request_type'] = "assistance_request"

    Staff.objects[2].update(push__requests_queue=returning_dict)
    push_assistance_request_notification(returning_dict)
    returning_dict['msg'] = "Service has been requested"
    #socket_io.emit('assist', json_util.dumps(returning_dict), room=user_obj.current_table_id, namespace=our_namespace)
    socket_io.emit('assist', json_util.dumps(returning_dict), namespace=our_namespace)
