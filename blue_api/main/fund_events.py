import sys
from . import main
from flask import session, request
from .. import socket_io, our_namespace
from backend.mongo.query import *
import numpy as np
from flask_jwt_extended import (
    jwt_required, get_jwt_identity,
)
from flask_socketio import emit, join_room, leave_room, disconnect, rooms

all_clients = []
active_clients = []


@socket_io.on('connect', namespace=our_namespace)
@jwt_required
def connect():
    username = get_jwt_identity()
    app_user = AppUser.objects(username=username).first()
    previous_sid = app_user.sid
    if previous_sid:
        disconnect(previous_sid)
    if app_user.user_type == "manager":
        join_room(app_user.restaurant_id)
        Restaurant.objects(restaurant_id=app_user.restaurant_id).first().update(set__manager_room=app_user.restaurant_id)
    elif app_user.user_type == "kitchen":
        join_room(app_user.restaurant_id+"_kitchen")
        Restaurant.objects(restaurant_id=app_user.restaurant_id).first().update(set__kitchen_room=app_user.restaurant_id+"_kitchen")
    elif app_user.user_type == "staff":
        for table in Table.objects(staff__in=[app_user.staff_user.id]):
            join_room(str(table.id))
    elif app_user.user_type == "customer":
        join_room(str(app_user.rest_user.current_table_id))
    AppUser.objects(username=username).first().update(set__sid=request.sid)
    sys.stderr.write("LiQR_Error: "+username+" who is a "+app_user.user_type+" connected\n")
    # all_clients.append(request.sid)


@socket_io.on('disconnect', namespace=our_namespace)
def on_disconnect():
    # print("Disconnected :( from ", request.sid)
    return


@socket_io.on('check_logger', namespace=our_namespace)
def fetch_all(message):
    emit('logger', {'msg': "Event fetch is workign HERE IT IS TABLE      " + str(np.random.randint(100))}, )
