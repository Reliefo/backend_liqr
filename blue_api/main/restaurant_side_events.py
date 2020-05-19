import traceback
from flask import request
from flask_socketio import emit
from .. import socket_io, our_namespace
from backend.mongo.query import *
from werkzeug.security import generate_password_hash
from backend.aws_api.sns_pub import push_order_complete_notification, push_assistance_request_notification


@socket_io.on('fetch_rest_manager', namespace=our_namespace)
def fetch_rest_object(message):
    input_dict = json_util.loads(message)
    restaurant_id = input_dict['restaurant_id']
    rest_json = return_restaurant(restaurant_id)
    emit('restaurant_object', rest_json)
    lists_json = Restaurant.objects.filter(restaurant_id=restaurant_id).first().fetch_order_lists()

    emit('order_lists', lists_json)


@socket_io.on('fetch_order_lists', namespace=our_namespace)
def fetch_order_lists(message):
    input_dict = json_util.loads(message)
    restaurant_id = input_dict['restaurant_id']
    lists_json = Restaurant.objects.filter(restaurant_id=restaurant_id).first().fetch_order_lists()

    emit('order_lists', lists_json)


@socket_io.on('fetch_kitchen_details', namespace=our_namespace)
def fetch_kitchen_details(message):
    input_dict = json_util.loads(message)
    restaurant_id = input_dict['restaurant_id']
    kitchen_staff_id = input_dict['kitchen_staff_id']
    emit('kitchen_staff_object', KitchenStaff.objects.exclude('orders_cooked').get(id=kitchen_staff_id).to_json())
    lists_json = Restaurant.objects.filter(restaurant_id=restaurant_id).first().fetch_order_lists()
    emit('order_lists', lists_json)


@socket_io.on('configuring_restaurant', namespace=our_namespace)
def configuring_restaurant_event(message):
    restaurant_id = AppUser.objects(sid=request.sid).first().restaurant_id
    manager_room = Restaurant.objects.filter(restaurant_id=restaurant_id).first().manager_room
    output = configuring_restaurant(json_util.loads(message))
    emit('updating_config', json_util.dumps(output),
         room=manager_room)


@socket_io.on('kitchen_updates', namespace=our_namespace)
def send_new_orders(message):
    restaurant_object = Restaurant.objects.filter(table_orders__in=[message['table_order_id']]).first()
    status_tuple = (message['table_order_id'], message['order_id'], message['food_id'])
    if message['type'] == 'cooking':
        order_status_cooking(status_tuple)
    else:
        order_status_completed(status_tuple)

    table_order = TableOrder.objects.get(id=status_tuple[0])
    ordered_by = Order.objects.get(id=status_tuple[1]).placed_by['name']
    food_name = FoodItem.objects.get(id=status_tuple[2]).name

    sending_dict = {'table_order_id': status_tuple[0], 'type': message['type'], 'order_id': status_tuple[1],
                    'food_id': status_tuple[2], 'kitchen_staff_id': message['kitchen_staff_id'],
                    "table": table_order.table,
                    'table_id': table_order.table_id, 'user': ordered_by, 'timestamp': str(datetime.now()),
                    'food_name': food_name}

    if sending_dict['type'] == 'completed':
        sending_dict['request_type'] = "pickup_request"
        sending_dict['status'] = "pending"
        KitchenStaff.objects.get(id=message['kitchen_staff_id']).update(push__orders_cooked=sending_dict)
        for staff in Table.objects.get(id=table_order.table_id).staff:
            if staff.endpoint_arn:
                staff.requests_queue.append(sending_dict)
                push_order_complete_notification(sending_dict, staff.endpoint_arn)
            staff.save()

    sending_json = json_util.dumps(sending_dict)
    socket_io.emit('order_updates', sending_json, room=restaurant_object.manager_room, namespace=our_namespace)
    socket_io.emit('order_updates', sending_json, room=restaurant_object.kitchen_room, namespace=our_namespace)
    socket_io.emit('order_updates', sending_json, room=table_order.table_id, namespace=our_namespace)
    emit('logger', {'msg': message})


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
        if input_dict['status'] == "rejected":
            socket_io.emit('order_updates', json_util.dumps(input_dict), namespace=our_namespace)
            curr_staff.rej_order_history.append(input_dict)
            push_order_complete_notification(input_dict, curr_staff.endpoint_arn)
            curr_staff.save()
            return
        elif input_dict['status'] == "accepted_rejected":
            input_dict['status'] = 'accepted'
            curr_staff.order_history.remove(input_dict)
            input_dict['status'] = 'rejected'
            curr_staff.rej_order_history.append(input_dict)
            push_order_complete_notification(input_dict, curr_staff.endpoint_arn)
            curr_staff.save()
            return
        else:
            input_dict['type'] = 'on_the_way'
            curr_staff.order_history.append(input_dict)
            socket_io.emit('order_updates', json_util.dumps(input_dict), namespace=our_namespace)
            curr_staff.save()
            return
    if input_dict['request_type'] == 'assistance_request':
        curr_staff = Staff.objects.get(id=input_dict['staff_id'])
        input_dict['staff_name'] = curr_staff.name
        requests_queue = curr_staff.requests_queue
        for n, request in enumerate(requests_queue):
            if request['request_type'] == 'assistance_request':
                if request['assistance_req_id'] == input_dict['assistance_req_id']:
                    requests_queue.pop(n)
        curr_staff.requests_queue = requests_queue
        if input_dict['status'] == "rejected":
            Staff.objects.get(id=input_dict['staff_id']).update(push__rej_assistance_history=input_dict)
            push_assistance_request_notification(input_dict, curr_staff.endpoint_arn)
            socket_io.emit('assist', json_util.dumps(input_dict), namespace=our_namespace)
            curr_staff.save()
            return
        elif input_dict['status'] == "accepted_rejected":
            input_dict['status'] = 'accepted'
            Staff.objects.get(id=input_dict['staff_id']).update(pull__assistance_history=input_dict)
            input_dict['status'] = 'rejected'
            Staff.objects.get(id=input_dict['staff_id']).update(push__rej_assistance_history=input_dict)
            push_assistance_request_notification(input_dict, curr_staff.endpoint_arn)
            curr_staff.save()
            return
        else:
            Assistance.objects.get(id=input_dict['assistance_req_id']).update(
                set__accepted_by={'staff_id': str(curr_staff.id), 'staff_name': curr_staff.name})
            curr_staff.assistance_history.append(input_dict)
            staff_id = input_dict.pop('staff_id')
            input_dict['accepted_py'] = {'staff_id': staff_id, 'staff_name': curr_staff.name}
            input_dict['msg'] = "Service has been accepted"
            socket_io.emit('assist', json_util.dumps(input_dict), namespace=our_namespace)
            curr_staff.save()
            return


@socket_io.on('fetch_staff_details', namespace=our_namespace)
def fetch_staff_details(message):
    socket_io.emit('logger', message, namespace=our_namespace)
    user_rest_dets = json_util.loads(message)
    staff_id = user_rest_dets['staff_id']
    rest_id = user_rest_dets['restaurant_id']
    emit('staff_details', return_staff_details(staff_id))
    emit('restaurant_object', return_restaurant(rest_id))


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
        AppUser(username=input_dict["username"], password=hash_pass, room=assigned_room,
                user_type=input_dict['user_type'], restaurant_id=rest_id, temp_password=True,
                staff_user=Staff.objects.get(id=input_dict['object_id']).to_dbref()).save()
    elif input_dict['user_type'] == "kitchen":
        AppUser(username=input_dict["username"], password=hash_pass, room=assigned_room,
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
    if billed_cleaned(table_id):
        input_dict['status'] = 'billed'
        emit('billing', json_util.dumps(input_dict))
    else:
        input_dict['status'] = 'failed'
        emit('billing', json_util.dumps(input_dict))
