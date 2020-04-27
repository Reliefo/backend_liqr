import traceback

from flask_socketio import emit
from .. import socket_io, our_namespace
from backend.mongo.query import *
from backend.aws_api.sns_pub import push_order_complete_notification


@socket_io.on('rest_with_id', namespace=our_namespace)
def fetch_rest_object(message):
    rest_json = return_restaurant(message)
    emit('restaurant_object', rest_json)


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


@socket_io.on('configuring_restaurant', namespace=our_namespace)
def configuring_restaurant_event(message):
    print("IT's WORKING")
    output = configuring_restaurant(json_util.loads(message))
    print(message)
    emit('updating_config', json_util.dumps(output))


@socket_io.on('kitchen_updates', namespace=our_namespace)
def send_new_orders(message):
    status_tuple = (message['table_order_id'], message['order_id'], message['food_id'])
    if message['type'] == 'cooking':
        order_status_cooking(status_tuple)
    else:
        order_status_completed(status_tuple)

    sending_dict = {'table_order_id': status_tuple[0], 'type': message['type'], 'order_id': status_tuple[1],
                    'food_id': status_tuple[2], 'kitchen_app_id': message['kitchen_app_id']}

    if sending_dict['type'] == 'completed':
        push_order_complete_notification(sending_dict)

    sending_json = json_util.dumps(sending_dict)
    socket_io.emit('order_updates', sending_json, namespace=our_namespace)
    emit('fetch', {'msg': message})


@socket_io.on('staff_acceptance', namespace=our_namespace)
def staff_acceptance(message):
    input_dict = json_util.loads(message)
    if input_dict['status'] == "rejected":
        socket_io.emit('order_updates', json_util.dumps(input_dict), namespace=our_namespace)
        return
    accepted_by = input_dict['staff_id']

    input_dict['type'] = 'on_the_way'
    socket_io.emit('order_updates', json_util.dumps(input_dict), namespace=our_namespace)
