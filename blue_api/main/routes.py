from flask import request, jsonify, redirect, render_template

from backend.mongo.mongo_setup import setup_mongo
from . import main
from .. import login_manager
from flask_login import login_required, logout_user
from backend.mongo.query import *

from flask_cognito import cognito_auth_required, current_user, current_cognito_jwt

@main.route('/')
def hello_world():
    return redirect("https://solutions.liqr.cc/")


@main.route('/rest_<int:rest_no>', methods=['GET'])
#@login_required
def fetch_restaurant(rest_no):
    rest_json = Restaurant.objects[rest_no].to_json()
    # socket_io.emit('restaurant_object', rest_json, namespace=our_namespace)
    return rest_json


@main.route('/rest_no', methods=['GET'])
#@login_required
def fetch_restaurant_no(rest_no):
    rest_no_json=json_util.dumps(([{rest.name:n} for n,rest in enumerate(Restaurant.objects)]))
    # socket_io.emit('restaurant_object', rest_json, namespace=our_namespace)
    return rest_no_json


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
    if table_no == 3:
        table_no = 41
    return redirect("https://order.liqr.cc/?table_id=" + str(Table.objects[table_no].id))

@main.route('/rt/<int:rest_no>_<int:table_no>', methods=['GET'])
def rest_table_no(rest_no,table_no):
    table_id = str(Restaurant.objects[rest_no].tables[table_no].id)
    return redirect("https://order.liqr.cc/?table_id=" + table_id)



@main.route('/local/<int:table_no>', methods=['GET'])
def local_no(table_no):
    if table_no == 3:
        table_no = 41
    return redirect("http://localhost:3000/?table_id=" + str(Table.objects[table_no].id))


@main.route('/x_<string:table_id>', methods=['GET'])
def shortened_table_id(table_id):
    actual_table_id=Table.objects.get(tid=table_id).id
    return redirect("https://order.liqr.cc/?table_id=" + str(actual_table_id))


@main.route('/bridge_socket', methods=['GET'])
def bridge_socket():
    return render_template('index.html')
