from .. import socket_io, our_namespace
from backend.mongo.query import *
from flask_socketio import emit
from backend.aws_api.sns_pub import push_assistance_request_notification


@socket_io.on('fetch_rest_customer', namespace=our_namespace)
def fetch_rest_customer(message):
    socket_io.emit('logger', message, namespace=our_namespace)
    user_rest_dets = json_util.loads(message)
    user_id = user_rest_dets['user_id']
    rest_id = user_rest_dets['restaurant_id']
    emit('user_details', return_user_details(user_id))
    emit('table_details', return_table_details(user_id))
    # TODO Remove this after frontend integraton
    emit('restaurant_object', return_restaurant_customer(rest_id))
    emit('home_screen_lists', home_screen_lists(rest_id))


@socket_io.on('place_personal_order', namespace=our_namespace)
def place_personal_order(message):
    input_order = json_util.loads(message)
    socket_io.emit('logger', message, namespace=our_namespace)
    new_order = order_placement(input_order)
    new_order_dict = json_util.loads(new_order)
    restaurant_object = Restaurant.objects.filter(tables__in=[new_order_dict['table_id']]).first()
    socket_io.emit('new_orders', new_order, room=restaurant_object.manager_room, namespace=our_namespace)
    socket_io.emit('new_orders', new_order, room=restaurant_object.kitchen_room, namespace=our_namespace)
    socket_io.emit('new_orders', new_order, room=new_order_dict['table_id'], namespace=our_namespace)


@socket_io.on('push_to_table_cart', namespace=our_namespace)
def push_to_table(message):
    input_order = json_util.loads(message)
    socket_io.emit('logger', message, namespace=our_namespace)
    push_to_table_cart(input_order)
    table_cart_order = Table.objects.get(id=input_order['table']).table_cart.to_json()
    socket_io.emit('table_cart_orders', table_cart_order, namespace=our_namespace)
    socket_io.emit('table_cart_orders', table_cart_order, room=table_cart_order.table_id, namespace=our_namespace)


@socket_io.on('place_table_order', namespace=our_namespace)
def place_table_order(message):
    table_id_dict = json_util.loads(message)
    socket_io.emit('logger', table_id_dict, namespace=our_namespace)
    table_id = table_id_dict['table_id']
    socket_io.emit('logger', message, namespace=our_namespace)
    new_order = order_placement_table(table_id)
    new_order_dict = json_util.loads(new_order)
    restaurant_object = Restaurant.objects.filter(tables__in=[new_order_dict['table_id']]).first()
    socket_io.emit('new_orders', new_order, room=restaurant_object.manager_room, namespace=our_namespace)
    socket_io.emit('new_orders', new_order, room=restaurant_object.kitchen_room, namespace=our_namespace)
    socket_io.emit('new_orders', new_order, room=new_order_dict['table_id'], namespace=our_namespace)


"""
@socket_io.on('kitchen_updates', namespace=our_namespace)
socket_io.emit('order_updates')
"""


@socket_io.on('assistance_requests', namespace=our_namespace)
def assistance_requests(message):
    input_dict = json_util.loads(message)
    socket_io.emit('logger', message, namespace=our_namespace)
    assistance_ob = assistance_req(input_dict)
    returning_message = assistance_ob.to_json()

    restaurant_object = Restaurant.objects.filter(tables__in=[input_dict['table']]).first()
    restaurant_object.assistance_reqs.append(assistance_ob.to_dbref())
    restaurant_object.save()
    returning_dict = json_util.loads(returning_message)
    returning_dict['request_type'] = "assistance_request"
    returning_dict['status'] = "pending"
    restaurant_object.assistance_reqs.append(returning_dict)
    table = Table.objects.get(id=input_dict['table'])
    table.requests_queue.append(returning_dict)
    for staff in table.staff:
        if staff.endpoint_arn:
            returning_dict['staff_id'] = staff.id
            push_assistance_request_notification(returning_dict, staff.endpoint_arn)
        staff.save()
    table.save()

    returning_dict['msg'] = "Service has been requested"
    socket_io.emit('assist', json_util.dumps(returning_dict), room=returning_dict['table_id'], namespace=our_namespace)
    socket_io.emit('assist', json_util.dumps(returning_dict), room=restaurant_object.manager_room,
                   namespace=our_namespace)


@socket_io.on('fetch_the_bill', namespace=our_namespace)
def fetch_the_bill(message):
    input_dict = json_util.loads(message)
    socket_io.emit('logger', message, namespace=our_namespace)
    user_id = input_dict['user_id']
    if input_dict['table_bill']:
        returning_json = json_util.dumps({'status': "fetching_bill", 'message': 'Your table bill will be brought to you'})
        socket_io.emit('billing', returning_json, namespace=our_namespace)
    else:
        returning_json = json_util.dumps({'status': "fetching_bill", 'message': 'Your personal bill will be brought '
                                                                                'to you'})
        socket_io.emit('billing', returning_json, namespace=our_namespace)
