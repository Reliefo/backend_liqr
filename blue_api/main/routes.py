from flask import request, jsonify, redirect

from backend.mongo.mongo_setup import setup_mongo
from . import main
from backend.mongo.query import *


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


@main.route('/mongo_setup', methods=['GET'])
def mongo_setup():
    setup_mongo()
    return "All data has been pushed to mongo"


@main.route('/clear_orders', methods=['GET'])
def clear_orders():
    for order in Order.objects:
        order.delete()

    for order in TableOrder.objects:
        order.delete()
    return "Cleared orders"


@main.route('/get_just_menu/<string:jm_id>', methods=['GET'])
def get_just_menu(jm_id):
    jm = JustMenu.objects.get(id=jm_id)
    jm.visits.append(datetime.now())
    jm.save()
    return jm.to_json()


@main.route('/table/<string:table_id>', methods=['GET'])
def scanned_table(table_id):
    return redirect("https://order.liqr.cc/?table_id=" + table_id)


@main.route('/table_no/<int:table_no>', methods=['GET'])
def scanned_table_no(table_no):
    if table_no==3:
        table_no=41
    return redirect("https://order.liqr.cc/?table_id=" + str(Table.objects[table_no].id))
