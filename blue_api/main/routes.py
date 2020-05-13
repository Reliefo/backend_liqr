from flask import request, jsonify, redirect

from backend.mongo.mongo_setup import setup_mongo
from . import main
from backend.mongo.query import *
from .. import socket_io, our_namespace


@main.route('/')
def hello_world():
    return redirect("https://solutions.liqr.cc/")


@main.route('/rest')
def fetch_restaurant():
    rest_json = return_restaurant("BNGHSR0001")
    # socket_io.emit('restaurant_object', rest_json, namespace=our_namespace)
    return rest_json


@main.route('/bill', methods=['GET'])
def fetch_orders2():
    billed_cleaned('5eb41b91adb66da6f5312125')
    return "Sending"


@main.route('/send_cooking_updates', methods=['POST'])
def cooking_updates():
    # socket_io.emit('fetch',{'hey':'asdfsdf'},namespace=our_namespace)
    status_tuple = pick_order()

    order_status_cooking(status_tuple)

    sending_dict = {'table_order_id': status_tuple[0], 'type': 'cooking', 'order_id': status_tuple[1],
                    'food_id': status_tuple[2]}
    if len(status_tuple) == 4:
        sending_dict['food_options_id'] = status_tuple[3]
    sending_json = json_util.dumps(sending_dict)
    socket_io.emit('order_updates', sending_json, namespace=our_namespace)

    return sending_json


@main.route('/send_completed_updates', methods=['POST'])
def completed_updates():
    # socket_io.emit('fetch',{'hey':'asdfsdf'},namespace=our_namespace)
    status_tuple = pick_order2()

    order_status_completed(status_tuple)

    sending_dict = {'table_order_id': status_tuple[0], 'type': 'completed', 'order_id': status_tuple[1],
                    'food_id': status_tuple[2]}
    sending_json = json_util.dumps(sending_dict)
    socket_io.emit('order_updates', sending_json, namespace=our_namespace)

    return sending_json


@main.route('/assist', methods=['POST'])
def assist_them():
    assistance_ob = assistance_req(generate_asstype())
    socket_io.emit('assist', assistance_ob.to_json(), namespace=our_namespace)
    staff_name = send_assistance_req(str(assistance_ob.id))
    returning_message = assistance_ob.to_json()
    returning_dict = json_util.loads(returning_message)
    returning_dict['msg'] = "Service has been acceptewafnsdovn"
    socket_io.emit('assist', json_util.dumps(returning_dict), namespace=our_namespace)
    time.sleep(1)

    socket_io.emit('assist_updates', {'assistance_id': str(assistance_ob.id), 'staff_name': staff_name},
                   namespace=our_namespace)
    return str(assistance_ob.to_json()) + ' ' + staff_name


@main.route('/mongo_setup', methods=['GET'])
def mongo_setup():
    setup_mongo()
    return "All data has been pushed to mongo"


@main.route('/user_scan', methods=['POST'])
def user_scan_portal():
    content = request.json
    table_no = content['table']
    unique_id = content['unique_id']
    table_id = str(Table.objects[int(table_no)].id)
    user_id = str(user_scan(table_id, unique_id))
    socket_io.emit('user_scan', json_util.dumps({"table_no": table_no, "user_id": user_id, "table_id": table_id}),
                   namespace=our_namespace)
    return json_util.dumps({"table_no": table_no, "user_id": user_id, "table_id": table_id})


@main.route('/clear_orders', methods=['GET'])
def clear_orders():
    for order in Order.objects:
        order.delete()

    for order in TableOrder.objects:
        order.delete()
    return "Cleared orders"


@main.route('/table/<string:table_id>', methods=['GET'])
def scanned_table(table_id):
    return redirect("https://order.liqr.cc/?table_id=" + table_id)


@main.route('/table_no/<int:table_no>', methods=['GET'])
def scanned_table_no(table_no):
    return redirect("https://order.liqr.cc/?table_id=" + str(Table.objects[table_no].id))
