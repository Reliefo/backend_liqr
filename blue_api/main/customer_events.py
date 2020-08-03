from .. import socket_io, our_namespace
from backend.mongo.query import *
from flask_socketio import emit
import sys
from backend.aws_api.sns_pub import push_assistance_request_notification, push_bill_request_notification


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
    emit('home_screen_lists', fetch_home_screen_lists(rest_id))


@socket_io.on('place_personal_order', namespace=our_namespace)
def place_personal_order(message):
    input_order = json_util.loads(message)
    sys.stderr.write("LiQR_Error: " + message + " was sent to customer events\n")
    socket_io.emit('logger', message, namespace=our_namespace)
    new_order = order_placement(input_order)
    new_order_dict = json_util.loads(new_order)
    restaurant_object = Restaurant.objects.filter(tables__in=[new_order_dict['table_id']]).first()
    socket_io.emit('new_orders', new_order, room=restaurant_object.manager_room, namespace=our_namespace)
    socket_io.emit('new_orders', new_order, room=restaurant_object.kitchen_room, namespace=our_namespace)
    socket_io.emit('new_orders', new_order, room=new_order_dict['table_id'], namespace=our_namespace)


@socket_io.on('push_to_table_cart', namespace=our_namespace)
def push_to_table(message):
    """{
    "table": "5eccc49668b1b9d33f7108ac",
    "orders": [
        {
            "placed_by": "5ece0b5f25e42280c6d83951",
            "food_list": [
                {
                    "name": "Nachos",
                    "description": "Nachos with extra toppings. Chicken or veg. With cheese",
                    "price": "190",
                    "restaurant_id": "BNGHSR0004",
                    "quantity": 1,
                    "food_id": "5eccc9a668b1b9d33f7108b3",
                    "food_options": {
                        "options": [
                            {
                                "option_name": "Veg",
                                "option_price": "190"
                            }
                        ],
                        "choices": [
                            "Mozzarella"
                        ]
                    }
                }
            ]
        }
    ]
}"""
    input_order = json_util.loads(message)
    sys.stderr.write("LiQR_Error: " + message + " was sent to customer events\n")
    socket_io.emit('logger', message, namespace=our_namespace)
    push_to_table_cart(input_order)
    table_cart_order = Table.objects.get(id=input_order['table']).table_cart.to_json()
    socket_io.emit('table_cart_orders', table_cart_order, room=input_order['table'], namespace=our_namespace)


@socket_io.on('remove_table_cart', namespace=our_namespace)
def remove_table_cart(message):
    """Needs:
    table_id
    order_id
    food_id"""
    input_order = json_util.loads(message)
    sys.stderr.write("LiQR_Error: " + message + " was sent to customer events\n")
    socket_io.emit('logger', message, namespace=our_namespace)
    remove_from_table_cart(input_order)
    table_cart_order = Table.objects.get(id=input_order['table_id']).table_cart.to_json()
    socket_io.emit('table_cart_orders', table_cart_order, room=input_order['table_id'], namespace=our_namespace)


@socket_io.on('place_table_order', namespace=our_namespace)
def place_table_order(message):
    table_id_dict = json_util.loads(message)
    table_id = table_id_dict['table_id']
    socket_io.emit('logger', message, namespace=our_namespace)
    new_order = order_placement_table(table_id)
    new_order_dict = json_util.loads(new_order)
    restaurant_object = Restaurant.objects.filter(tables__in=[new_order_dict['table_id']]).first()
    socket_io.emit('new_orders', new_order, room=restaurant_object.manager_room, namespace=our_namespace)
    socket_io.emit('new_orders', new_order, room=restaurant_object.kitchen_room, namespace=our_namespace)
    socket_io.emit('new_orders', new_order, room=new_order_dict['table_id'], namespace=our_namespace)


@socket_io.on('cancel_ordered_items', namespace=our_namespace)
def cancel_items(message):
    input_order = json_util.loads(message)
    sys.stderr.write("LiQR_Error: " + message + " was sent to customer events\n")
    socket_io.emit('logger', message, namespace=our_namespace)
    input_order['status'] = 'cancelled'
    Order.objects.get(id=input_order['order_id']).update(pull__food_list=FoodItemMod(food_id=input_order['food_id']))
    input_order['table_orders'] = \
        json_util.loads(Table.objects.only("table_orders").get(id=input_order['table_id']).to_json())['table_orders']
    socket_io.emit('cancel_items_request', json_util.dumps(input_order), room=input_order['table_id'],
                   namespace=our_namespace)


"""
@socket_io.on('kitchen_updates', namespace=our_namespace)
socket_io.emit('order_updates')
"""


@socket_io.on('assistance_requests', namespace=our_namespace)
def assistance_requests(message):
    input_dict = json_util.loads(message)
    sys.stderr.write("LiQR_Error: " + message + " was sent to customer events\n")
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
            returning_message = push_assistance_request_notification(returning_dict, staff.endpoint_arn)
            if returning_message!='sent':
                sys.stderr.write("LiQR_Notification_Error: " + returning_message + " was sent to customer events\n"+staff.to_json())
    if input_dict['after_billing']:
        clear_table(str(table.id))
    table.save()

    returning_dict['msg'] = "Service has been requested"
    # socket_io.emit('assist', json_util.dumps(returning_dict), room=returning_dict['table_id'], namespace=our_namespace)
    emit('assist', json_util.dumps(returning_dict), namespace=our_namespace)
    socket_io.emit('assist', json_util.dumps(returning_dict), room=restaurant_object.manager_room,
                   namespace=our_namespace)


@socket_io.on('fetch_the_bill', namespace=our_namespace)
def fetch_the_bill(message):
    input_dict = json_util.loads(message)
    table_id = input_dict['table_id']
    table = Table.objects.get(id=table_id)
    user = User.objects.get(id=input_dict['user_id'])
    restaurant_object = Restaurant.objects.filter(tables__in=[table_id]).first()
    if input_dict['table_bill']:
        billed_return = billed_cleaned(table_id)
        returning_dict = {'status': "billed", 'table_id': table_id, 'table': table.name, 'user': user.name,
                          'order_history': json_util.loads(billed_return['order_history']),
                          'message': 'Your table bill will be brought to you'}
        returning_json = json_util.dumps(returning_dict)
        socket_io.emit('billing', returning_json, room=table_id, namespace=our_namespace)
        socket_io.emit('billing', returning_json, room=restaurant_object.manager_room, namespace=our_namespace)
        socket_io.emit('assist', returning_json, room=restaurant_object.manager_room, namespace=our_namespace)
        returning_dict.pop('order_history')
        for staff in table.staff:
            if staff.endpoint_arn:
                returning_dict['staff_id'] = str(staff.id)
                push_bill_request_notification(returning_dict, staff.endpoint_arn)
    else:
        returning_json = json_util.dumps(
            {'status': "billed", 'table_id': table_id, 'table': table.name, 'user': user.name,
             'message': 'Your personal bill will be brought to you', 'order_history': 'dud'})
        socket_io.emit('billing', returning_json, room=table_id, namespace=our_namespace)
        socket_io.emit('assist', returning_json, room=restaurant_object.manager_room,
                       namespace=our_namespace)
