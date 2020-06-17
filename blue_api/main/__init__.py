from flask import Blueprint

main = Blueprint('main', __name__)

from . import routes, login_routes, connect_event, kitchen_events, staff_events, manager_events, customer_events, \
    justmenu, cognito
