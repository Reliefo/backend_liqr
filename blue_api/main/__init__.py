from flask import Blueprint

main = Blueprint('main', __name__)

from . import routes, login_routes, fund_events, restaurant_side_events, customer_events

