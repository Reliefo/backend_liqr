from flask import request, jsonify, redirect, render_template

from . import main
from .. import login_manager
from flask_login import login_required, logout_user, current_user
from backend.mongo.query import *
from backend.constants.theme_constants import *
from flask_jwt_extended import (
    get_jwt_identity, jwt_required, create_access_token, create_refresh_token, jwt_refresh_token_required
)
import stripe
from flask_cognito import cognito_auth_required, current_cognito_jwt

# Set your secret key. Remember to switch to your live secret key in production!
# See your keys here: https://dashboard.stripe.com/account/apikeys
stripe.api_key = 'sk_test_51H4JNtEjtenrp5aUOHdImobYzp3B1ugG5gl1hzh5ZMpTXD2WEO9Ze6vcbyQjk5CKbNhZmzWSkDkLHiaHJhDgcnR800Z9F7xhJ1'
test_id = ''


@main.route('/secret', methods=['POST'])
def client_secret():
    table_id = request.form['table_id']
    table_ob = Table.objects.get(id=table_id)
    # ... Create or retrieve the PaymentIntent
    total_amount = int(table_ob.billing['total_bill'])
    intent = stripe.PaymentIntent.create(
        amount=total_amount*100,
        currency='usd',
        # Verify your integration in this guide by including this parameter
        metadata={'integration_check': 'accept_a_payment'},
    )
    table_ob.billing['client_secret'] = intent.client_secret
    table_ob.save()
    return jsonify(client_secret=intent.client_secret, total_amount=total_amount)


@main.route('/secret_check', methods=['POST'])
def client_secret_check():
    # retrieve the PaymentIntent
    table_id = request.form['table_id']
    table_ob = Table.objects.get(id=table_id)
    payment_intent = stripe.PaymentIntent.retrieve(table_ob.billing['client_secret'].split('_secret_')[0])
    return jsonify(payment_intent['status'])


@main.route('/')
def hello_world():
    return redirect("https://solutions.liqr.cc/")


@main.route('/rest_<int:rest_no>', methods=['GET'])
@login_required
# @cognito_auth_required
def fetch_restaurant(rest_no):
    print(current_user)
    rest_json = Restaurant.objects[rest_no].to_json()
    return rest_json


@main.route('/phone_login', methods=['POST'])
@login_required
def phone_login():
    if request.method == 'POST':
        username = current_user.username
        user_id = str(current_user.rest_user.id)
        unique_id = request.form['unique_id']
        table_id = request.form['table_id']
        restaurant_object = Restaurant.objects.filter(tables__in=[table_id])[0]

        user_scan_otp(table_id, user_id)
        this_user = User.objects.get(id=current_user.rest_user.id)
        name = this_user.name
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)
        return json_util.dumps(
            {"status": "Registration successful", "jwt": access_token, "refresh_token": refresh_token, "code": "200",
             "name": name, "unique_id": unique_id, "user_id": user_id, "table_id": table_id,
             "restaurant_id": restaurant_object.restaurant_id})
    return "asdf"


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
        theme_properties = {'theme': True, 'variables': variables}
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


@main.route('/rtl/<int:rest_no>_<int:table_no>', methods=['GET'])
def rest_table_no_local(rest_no, table_no):
    table_id = str(Restaurant.objects[rest_no].tables[table_no].id)
    return redirect("http://localhost:3000/?table_id=" + table_id)


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
    return render_template('bridge_index.html')


@main.route('/privacy_policy', methods=['GET'])
def privacy_policy():
    return render_template('privacy_policy.html')


@main.route('/terms_of_service', methods=['GET'])
def terms_of_service():
    return render_template('terms_of_service.html')
