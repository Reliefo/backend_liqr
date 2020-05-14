import threading
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
        Restaurant.objects(restaurant_id=app_user.restaurant_id).first().update(set__manager_room=request.sid)
    elif app_user.user_type == "kitchen":
        join_room(app_user.restaurant_id+"_kitchen")
        Restaurant.objects(restaurant_id=app_user.restaurant_id).first().update(set__kitchen_room=app_user.restaurant_id+"_kitchen")
    elif app_user.user_type == "staff":
        for table in Table.objects(staff__in=[app_user.staff_user.id]):
            join_room(str(table.id))
    elif app_user.user_type == "customer":
        join_room(str(app_user.rest_user.current_table_id))
    AppUser.objects(username=username).first().update(set__sid=request.sid)
    # all_clients.append(request.sid)


@socket_io.on('disconnect', namespace=our_namespace)
def on_disconnect():
    print("Disconnected :( from ", request.sid)


@socket_io.on('check_logger', namespace=our_namespace)
def fetch_all(message):
    print("here i am printing requiest id", request.sid, request.namespace)
    print(message)
    print(datetime.now())
    emit('logger', {'msg': "Event fetch is workign HERE IT IS TABLE      " + str(np.random.randint(100))}, )
