import traceback

from flask_socketio import emit
from .. import socket_io, our_namespace
from backend.mongo.query import *
from werkzeug.security import generate_password_hash
from backend.aws_api.sns_pub import push_order_complete_notification, push_assistance_request_notification


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
    output = configuring_restaurant(json_util.loads(message))
    emit('updating_config', json_util.dumps(output))


@socket_io.on('kitchen_updates', namespace=our_namespace)
def send_new_orders(message):
    status_tuple = (message['table_order_id'], message['order_id'], message['food_id'])
    if message['type'] == 'cooking':
        order_status_cooking(status_tuple)
    else:
        order_status_completed(status_tuple)

    table_order = TableOrder.objects.get(id=status_tuple[0])
    ordered_by = Order.objects.get(id=status_tuple[1]).placed_by.name
    food_name = FoodItem.objects.get(id=status_tuple[2]).name

    sending_dict = {'table_order_id': status_tuple[0], 'type': message['type'], 'order_id': status_tuple[1],
                    'food_id': status_tuple[2], 'kitchen_app_id': message['kitchen_app_id'], "table": table_order.table,
                    'table_id': table_order.table_id, 'user': ordered_by, 'timestamp': str(datetime.now()),
                    'food_name': food_name}

    if sending_dict['type'] == 'completed':
        sending_dict['request_type'] = "pickup_request"
        Staff.objects[2].update(push__requests_queue=sending_dict)
        push_order_complete_notification(sending_dict)

    sending_json = json_util.dumps(sending_dict)
    socket_io.emit('order_updates', sending_json, namespace=our_namespace)
    emit('fetch', {'msg': message})


@socket_io.on('staff_acceptance', namespace=our_namespace)
def staff_acceptance(message):
    input_dict = json_util.loads(message)
    if input_dict['request_type'] == 'pickup_request':
        curr_staff = Staff.objects.get(id=input_dict['staff_id'])
        requests_queue = curr_staff.requests_queue
        for n, request in enumerate(requests_queue):
            if request['request_type'] == 'pickup_request':
                if request['order_id'] == input_dict['order_id'] and request['food_id'] == input_dict['food_id']:
                    requests_queue.pop(n)
        curr_staff.requests_queue = requests_queue
        curr_staff.save()
        if input_dict['status'] == "rejected":
            socket_io.emit('order_updates', json_util.dumps(input_dict), namespace=our_namespace)
            Staff.objects.get(id=input_dict['staff_id']).update(push__rej_order_history=input_dict)
            push_order_complete_notification(input_dict)
            return
        else:
            input_dict['type'] = 'on_the_way'
            Staff.objects.get(id=input_dict['staff_id']).update(push__order_history=input_dict)
            socket_io.emit('order_updates', json_util.dumps(input_dict), namespace=our_namespace)
            return
    if input_dict['request_type'] == 'assistance_request':
        curr_staff = Staff.objects.get(id=input_dict['staff_id'])
        requests_queue = curr_staff.requests_queue
        for n, request in enumerate(requests_queue):
            if request['request_type'] == 'assistance_request':
                if request['assistance_req_id'] == input_dict['assistance_req_id']:
                    requests_queue.pop(n)
        curr_staff.requests_queue = requests_queue
        curr_staff.save()
        if input_dict['status'] == "rejected":
            Staff.objects.get(id=input_dict['staff_id']).update(push__rej_assistance_history=input_dict)
            push_assistance_request_notification(input_dict)
            socket_io.emit('assist', json_util.dumps(input_dict), namespace=our_namespace)
            return
        else:
            input_dict['msg'] = "Service has been accepted"
            Staff.objects.get(id=input_dict['staff_id']).update(push__assistance_history=input_dict)
            socket_io.emit('assist', json_util.dumps(input_dict), namespace=our_namespace)
            return


@socket_io.on('fetch_staff_details', namespace=our_namespace)
def fetch_staff_details(message):
    socket_io.emit('fetch', message, namespace=our_namespace)
    user_rest_dets = json_util.loads(message)
    staff_id = user_rest_dets['staff_id']
    rest_id = user_rest_dets['restaurant_id']
    emit('staff_details', return_staff_details(staff_id))
    emit('restaurant_object', return_restaurant(rest_id))


@socket_io.on('register_your_people', namespace=our_namespace)
def register_your_people(message):
    input_dict = json_util.loads(message)
    auth_user = AppUser.objects(username=input_dict["auth_username"]).first()
    if auth_user:
        rest_name = input_dict['restaurant_name']
        name = input_dict['name']
        hash_pass = generate_password_hash(input_dict["password"], method='sha255')
        assigned_room = "kids_room" if input_dict["username"][:2] == "KID" else "adults_room"
        if input_dict['user_type'] == "staff":
            AppUser(username=input_dict["username"], password=hash_pass, room=assigned_room,
                    user_type=input_dict['user_type'],
                    staff_user=Staff.objects.get(id=input_dict['object_id'])).save()
        elif input_dict['user_type'] == "kitchen":
            AppUser(username=input_dict["username"], password=hash_pass, room=assigned_room,
                    user_type=input_dict['user_type'],
                    kitchen_user=KitchenUser.objects.get(id=input_dict['object_id'])).save()
        else:
            return json_util.dumps({"status": "Registration failed"})
        input_dict['status'] = 'Registration successful'
        return json_util.dumps(input_dict)
