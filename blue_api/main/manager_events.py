import traceback
from flask import request
from flask_socketio import emit
from .. import socket_io, our_namespace
from backend.mongo.query import *
import sys
from werkzeug.security import generate_password_hash
from backend.aws_api.sns_pub import push_bill_request_notification


@socket_io.on('fetch_rest_manager', namespace=our_namespace)
def fetch_rest_object(message):
    input_dict = json_util.loads(message)
    restaurant_id = input_dict['restaurant_id']
    rest_json = return_restaurant(restaurant_id)
    emit('restaurant_object', rest_json)
    lists_json = Restaurant.objects.filter(restaurant_id=restaurant_id).first().fetch_order_lists()
    emit('order_lists', lists_json)


@socket_io.on('fetch_rest_owner', namespace=our_namespace)
def fetch_rest_owner(message):
    input_dict = json_util.loads(message)
    restaurant_id = input_dict['restaurant_id']
    rest_json = return_restaurant_owner(restaurant_id)
    emit('restaurant_object', rest_json)


@socket_io.on('configuring_restaurant', namespace=our_namespace)
def configuring_restaurant_event(message):
    restaurant_id = AppUser.objects(sid=request.sid).first().restaurant_id
    manager_room = Restaurant.objects.filter(restaurant_id=restaurant_id).first().manager_room
    output = configuring_restaurant(json_util.loads(message))
    emit('updating_config', json_util.dumps(output),
         room=manager_room)


@socket_io.on('register_your_people', namespace=our_namespace)
def register_your_people(message):
    input_dict = json_util.loads(message)
    rest_name = input_dict['restaurant_name']
    rest_id = input_dict['restaurant_id']
    name = input_dict['name']
    user_no = 0
    username_prefix = "SID" if input_dict['user_type'] == "staff" else "KID"
    username = username_prefix + rest_name[:3].upper() + name[:3].upper() + str(user_no)
    while len(AppUser.objects(username=username)) > 0:
        user_no += 1
        username = username_prefix + rest_name[:3].upper() + name[:3].upper() + str(user_no)
    password = username_prefix + rest_name[:3].upper() + name[:3].upper() + str(np.random.randint(420))
    input_dict['username'] = username
    input_dict['password'] = password
    hash_pass = generate_password_hash(password, method='sha256')
    assigned_room = "kids_room" if input_dict["username"][:2] == "KID" else "adults_room"
    if input_dict['user_type'] == "staff":
        AppUser(username=input_dict["username"], password=hash_pass,
                user_type=input_dict['user_type'], restaurant_id=rest_id, temp_password=True,
                staff_user=Staff.objects.get(id=input_dict['object_id']).to_dbref()).save()
    elif input_dict['user_type'] == "kitchen":
        AppUser(username=input_dict["username"], password=hash_pass,
                user_type=input_dict['user_type'], restaurant_id=rest_id, temp_password=True,
                kitchen_staff=KitchenStaff.objects.get(id=input_dict['object_id']).to_dbref()).save()
    else:
        emit('receive_your_people', json_util.dumps({"status": "Registration failed"}))
        return
    input_dict['status'] = 'Registration successful'
    emit('receive_your_people', json_util.dumps(input_dict))


@socket_io.on('bill_the_table', namespace=our_namespace)
def bill_the_table(message):
    input_dict = json_util.loads(message)
    table_id = input_dict['table_id']
    table = Table.objects.get(id=input_dict['table_id'])
    returning_dict = {'status': "billed", 'table_id': input_dict['table_id'], 'table': table.name, 'user': "Manager",
                      'order_history': json_util.loads(billed_cleaned(input_dict['table_id'])),
                      'message': 'Your table bill will be brought to you'}
    socket_io.emit('billing', json_util.dumps(returning_dict), namespace=our_namespace)
    returning_dict.pop('order_history')
    for staff in table.staff:
        if staff.endpoint_arn:
            push_bill_request_notification(returning_dict, staff.endpoint_arn)
