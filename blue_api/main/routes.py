from flask import request, jsonify, redirect, render_template

from . import main
from .. import login_manager
from flask_login import login_required, logout_user
from backend.mongo.query import *

from flask_cognito import cognito_auth_required, current_user, current_cognito_jwt

variables = {'--theme-font': 'Poppins',
  '--first-background-color': '#ffffff',
  '--second-background-color': '#ffffff',
  '--first-menu-background-color': '#f0f0f0',
  '--second-menu-background-color': '#f0f0f0',
  '--first-light-color': '#ffc967',
  '--second-light-color': '#ffa813',
  '--first-pattern-light-color': '#ffb023',
  '--second-pattern-light-color': '#ffb023',
  '--food-card-color': '#ffffff',
  '--welcome-card-color': '#ffffff',
  '--welcome-card-text-color': '#000000',
  '--food-menu-button-color': '#ffb023',
  '--add-button-color': '#ffb023',
  '--top-bar-color': '#ffb023',
  '--search-background-color': '#ffc45c',
  '--burger-menu-background-color': '#c0841d',
  '--first-footer-color': '#ffb023',
  '--second-footer-color': '#ffb023',
  '--categories-button-color': '#ffb023',
  '--categories-list-item-color': '#ffffff'}
variable_names = {'--theme-font': 'Theme Font, ignore this',
  '--first-background-color': 'Home Screen Background Color',
  '--second-background-color': 'Home Screen Background Color2',
  '--first-menu-background-color': 'Menu and Other Screens Background Color',
  '--second-menu-background-color': 'Menu and Other Screens Background Color2',
  '--first-light-color': 'Theme color which is blended for Need Help Choosing',
  '--second-light-color': 'Theme color which is blended for Need Help Choosing 2',
  '--first-pattern-light-color': 'Color for all other objects',
  '--second-pattern-light-color': 'COlor for all other objects 2',
  '--food-card-color': 'Food Item Card Color',
  '--welcome-card-color': 'Welcome to Restaurant Card Color',
  '--welcome-card-text-color': 'Welcome to Restaurant Text Color',
  '--food-menu-button-color': 'Full Menu Button color',
  '--add-button-color': 'Add button in food items color',
  '--top-bar-color': 'Top bar color',
  '--search-background-color': 'Search bar color',
  '--burger-menu-background-color': 'Side menu background color',
  '--first-footer-color': 'Footer color 1',
  '--second-footer-color': 'Footer color 1',
  '--categories-button-color': 'Floating categories button in menu screen color',
  '--categories-list-item-color': 'Floating categories item color'}

@main.route('/')
def hello_world():
    return redirect("https://solutions.liqr.cc/")


@main.route('/rest_<int:rest_no>', methods=['GET'])
# @login_required
def fetch_restaurant(rest_no):
    rest_json = Restaurant.objects[rest_no].to_json()
    return rest_json


@main.route('/rest_no', methods=['GET'])
# @login_required
def fetch_restaurant_no():
    rest_no_json = json_util.dumps(
        [{rest.name: str(n) + " " + rest.restaurant_id} for n, rest in enumerate(Restaurant.objects)])
    # socket_io.emit('restaurant_object', rest_json, namespace=our_namespace)
    return rest_no_json


@main.route('/set_theme', methods=['POST'])
def set_rest_theme():
    if request.method == "POST":
        restaurant_id = request.form['restaurant_id']
        variables = dict(request.form)
        variables.pop('restaurant_id')
        theme_properties = { 'theme':True, 'variables':variables }
        Restaurant.objects(restaurant_id=restaurant_id)[0].update(set__theme_properties=theme_properties)
        return redirect("https://liqr.cc/color?restaurant_id=" + restaurant_id)


@main.route('/color', methods=['GET'])
def color_picker():
    rest_names = [{'rest_name': rest.name, 'rest_no': str(n), 'rest_id': rest.restaurant_id} for n, rest in
                  enumerate(Restaurant.objects)]
    rest_id = request.args.get('restaurant_id')
    if rest_id:
        rest = Restaurant.objects(restaurant_id=rest_id)[0]
        theme_variables = {'rest_theme': rest.theme_properties, 'rest_id': rest.restaurant_id, 'rest_name': rest.name}
    else:
        rest = Restaurant.objects[0]
        theme_variables = {'rest_theme': rest.theme_properties, 'rest_id': rest.restaurant_id, 'rest_name': rest.name}
    return render_template(
        "color_pick.html",
        rest_names=rest_names,
        theme_variables=theme_variables,
        variables=variables,
        variable_names=variable_names
    )


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
def rest_table_no(rest_no, table_no):
    table_id = str(Restaurant.objects[rest_no].tables[table_no].id)
    return redirect("https://order.liqr.cc/?table_id=" + table_id)


@main.route('/local/<int:table_no>', methods=['GET'])
def local_no(table_no):
    if table_no == 3:
        table_no = 41
    return redirect("http://localhost:3000/?table_id=" + str(Table.objects[table_no].id))


@main.route('/x_<string:table_id>', methods=['GET'])
def shortened_table_id(table_id):
    actual_table_id = Table.objects.get(tid=table_id).id
    return redirect("https://order.liqr.cc/?table_id=" + str(actual_table_id))


@main.route('/bridge_socket', methods=['GET'])
def bridge_socket():
    return render_template('index.html')
