import traceback
from flask_socketio import emit
from .. import socket_io, our_namespace
from backend.mongo.query import *
import sys
from backend.aws_api.sns_pub import push_order_complete_notification, push_assistance_request_notification
from backend.aws_api.sns_registration import verify_endpoint


@socket_io.on('fetch_staff_details', namespace=our_namespace)
def fetch_staff_details(message):
    socket_io.emit('logger', message, namespace=our_namespace)
    user_rest_dets = json_util.loads(message)
    staff_id = user_rest_dets['staff_id']
    rest_id = user_rest_dets['restaurant_id']
    emit('staff_details', return_staff_details(staff_id))
    emit('restaurant_object', return_restaurant(rest_id))
    emit('requests_queue', fetch_requests_queue(staff_id, rest_id))
    lists_json = Restaurant.objects.filter(restaurant_id=rest_id).first().fetch_order_lists()
    emit('order_lists', lists_json)



@socket_io.on('staff_acceptance', namespace=our_namespace)
def staff_acceptance(message):
    input_dict = json_util.loads(message)
    curr_staff = Staff.objects.get(id=input_dict['staff_id'])
    table = Table.objects.get(id=input_dict['table_id'])

    requests_queue = table.requests_queue
    for n, n_request in enumerate(requests_queue):
        if n_request['request_type'] == input_dict['request_type']:
            if n_request['request_type'] == 'pickup_request':
                if n_request['order_id'] == input_dict['order_id'] and n_request['food_id'] == input_dict['food_id']:
                    requests_queue.pop(n)
            else:  # Assistance Request
                if n_request['assistance_req_id'] == input_dict['assistance_req_id']:
                    requests_queue.pop(n)
    table.requests_queue = requests_queue
    table.save()

    if input_dict['status'] == "rejected":
        curr_staff.rej_requests_history.append(input_dict)
        curr_staff.save()
        if input_dict['request_type'] == 'pickup_request':
            socket_io.emit('order_updates', json_util.dumps(input_dict), namespace=our_namespace)
            push_order_complete_notification(input_dict, curr_staff.endpoint_arn)
        else:  # Assistance Request
            socket_io.emit('assist', json_util.dumps(input_dict), namespace=our_namespace)
            push_assistance_request_notification(input_dict, curr_staff.endpoint_arn)
        return
    elif input_dict['status'] == "accepted_rejected":
        input_dict['status'] = 'accepted'
        curr_staff.requests_history.remove(input_dict)
        input_dict['status'] = 'rejected'
        curr_staff.rej_requests_history.append(input_dict)
        curr_staff.save()
        if input_dict['request_type'] == 'pickup_request':
            socket_io.emit('order_updates', json_util.dumps(input_dict), namespace=our_namespace)
            push_order_complete_notification(input_dict, curr_staff.endpoint_arn)
        else:  # Assistance Request
            socket_io.emit('assist', json_util.dumps(input_dict), namespace=our_namespace)
            push_assistance_request_notification(input_dict, curr_staff.endpoint_arn)
        return
    else:  # ACCEPTED

        if input_dict['request_type'] == 'pickup_request':
            input_dict['type'] = 'on_the_way'
            curr_staff.requests_history.append(input_dict)
            curr_staff.save()
            socket_io.emit('order_updates', json_util.dumps(input_dict), namespace=our_namespace)
            return
        else:  # Assistance Request
            Assistance.objects.get(id=input_dict['assistance_req_id']).update(
                set__accepted_by={'staff_id': str(curr_staff.id), 'staff_name': curr_staff.name})
            staff_id = input_dict.pop('staff_id')
            input_dict['accepted_by'] = {'staff_id': staff_id, 'staff_name': curr_staff.name}
            input_dict['msg'] = "Service has been accepted"
            curr_staff.requests_history.append(input_dict)
            curr_staff.save()
            socket_io.emit('assist', json_util.dumps(input_dict), namespace=our_namespace)
            return


@socket_io.on('check_endpoint', namespace=our_namespace)
def check_endpoint(message):
    input_dict = json_util.loads(message)
    if verify_endpoint(input_dict['staff_id']):
        input_dict['status'] = "working"
        emit('endpoint_check', json_util.dumps(input_dict))
    else:
        input_dict['status'] = "damaged"
        emit('endpoint_check', json_util.dumps(input_dict))
