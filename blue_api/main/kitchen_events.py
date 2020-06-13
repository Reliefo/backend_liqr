import traceback
from flask_socketio import emit
from .. import socket_io, our_namespace
from backend.mongo.query import *
from backend.aws_api.sns_pub import push_order_complete_notification


@socket_io.on('fetch_kitchen_details', namespace=our_namespace)
def fetch_kitchen_details(message):
    input_dict = json_util.loads(message)
    restaurant_id = input_dict['restaurant_id']
    kitchen_staff_id = input_dict['kitchen_staff_id']
    emit('kitchen_staff_object', KitchenStaff.objects.exclude('orders_cooked').get(id=kitchen_staff_id).to_json())
    emit('kitchen_object', Kitchen.objects.get(id=KitchenStaff.objects.only('id').only('name').get(id=kitchen_staff_id).kitchen).to_json())
    emit('restaurant_object', return_restaurant_kitchen(restaurant_id))
    lists_json = Restaurant.objects.filter(restaurant_id=restaurant_id).first().fetch_order_lists()
    emit('order_lists', lists_json)


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
    food_id = re.search('[a-z0-9]+', status_tuple[2]).group()
    food_name = FoodItem.objects.get(id=food_id).name

    sending_dict = {'table_order_id': status_tuple[0], 'type': message['type'], 'order_id': status_tuple[1],
                    'food_id': status_tuple[2], 'kitchen_staff_id': message['kitchen_staff_id'],
                    "table": table_order.table,
                    'table_id': table_order.table_id, 'user': ordered_by, 'timestamp': str(datetime.now()),
                    'food_name': food_name}

    if sending_dict['type'] == 'completed':
        sending_dict['request_type'] = "pickup_request"
        sending_dict['status'] = "pending"
        KitchenStaff.objects.get(id=message['kitchen_staff_id']).update(push__orders_cooked=sending_dict)
        table = Table.objects.get(id=table_order.table_id)
        table.requests_queue.append(sending_dict)
        for staff in table.staff:
            if staff.endpoint_arn:
                sending_dict['staff_id'] = staff.id
                push_order_complete_notification(sending_dict, staff.endpoint_arn)
        table.save()

    sending_json = json_util.dumps(sending_dict)
    socket_io.emit('order_updates', sending_json, room=restaurant_object.manager_room, namespace=our_namespace)
    socket_io.emit('order_updates', sending_json, room=restaurant_object.kitchen_room, namespace=our_namespace)
    socket_io.emit('order_updates', sending_json, room=table_order.table_id, namespace=our_namespace)
    emit('logger', {'msg': message})
