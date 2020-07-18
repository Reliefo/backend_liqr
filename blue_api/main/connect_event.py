import sys
from . import main
from flask import session, request
from .. import socket_io, our_namespace, cogauth
from backend.mongo.query import *
import numpy as np
from flask_jwt_extended import (
    jwt_required, get_jwt_identity,
)
from flask_socketio import emit, join_room, leave_room, disconnect, rooms


# configuration


# initialize extension

# @cogauth.identity_handler
# def lookup_cognito_user(payload):
#     """Look up user in our database from Cognito JWT payload."""
#     return AppUser.objects(username=payload['username'])



from flask_cognito import cognito_auth_required, current_user, current_cognito_jwt

# @route('/api/private')
# @cognito_auth_required
# def api_private():
#     # user must have valid cognito access or ID token in header
#     # (accessToken is recommended - not as much personal information contained inside as with idToken)
#     return jsonify({
#         'cognito_username': current_cognito_jwt['username'],   # from cognito pool
#         'user_id': current_user.id,   # from your database
#     })

@socket_io.on('connect', namespace=our_namespace)
#@jwt_required
# @cognito_auth_required
def connect():
    username = get_jwt_identity()
    #app_user = AppUser.objects(username=username).first()
    app_user = AppUser.objects.get(id="5f033493cfb1be420f5827a3")
    previous_sid = app_user.sid

    sys.stderr.write("LiQR_Error:  who is a "+str(request.args)+" connected\n")
    sys.stderr.write("LiQR_Error: "+username+" who is a "+app_user.user_type+" connected\n")
    if previous_sid:
        disconnect(previous_sid)
    if app_user.user_type == "manager":
        join_room(app_user.restaurant_id)
    elif app_user.user_type == "owner":
        join_room(app_user.restaurant_id)
    elif app_user.user_type == "kitchen":
        join_room(app_user.restaurant_id+"_kitchen")
    elif app_user.user_type == "staff":
        for table in Table.objects(staff__in=[app_user.staff_user.id]):
            join_room(str(table.id))
    elif app_user.user_type == "customer":
        sys.stderr.write("LiQR_Error: " +app_user.username)
        join_room(str(app_user.rest_user.current_table_id))
        try:
            sys.stderr.write("LiQR_Error: "+app_user.rest_user.name+" who is definitely a customer joined "+app_user.rest_user.current_table_id+"\n")
        except:
            pass
    AppUser.objects(username=app_user.username).first().update(set__sid=request.sid)
    sys.stderr.write("LiQR_Connection: "+app_user.username+" who is a "+app_user.user_type+" connected\n")


@socket_io.on('disconnect', namespace=our_namespace)
def on_disconnect():
    # print("Disconnected :( from ", request.sid)
    return


@socket_io.on('check_logger', namespace=our_namespace)
def fetch_all(message):
    emit('logger', {'msg': "Event fetch is workign HERE IT IS TABLE      " + str(np.random.randint(100))}, )
