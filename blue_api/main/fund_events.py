import threading
from . import main
from flask import session, request
from flask_socketio import emit, join_room, leave_room
from .. import socket_io, our_namespace
from backend.mongo.query import *
import numpy as np
from flask_jwt_extended import (
    jwt_required, get_jwt_identity,
    )

all_clients = []
active_clients = []


@socket_io.on('joined', namespace='/chat')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    join_room(room)
    emit('status', {'msg': session.get('name') + ' has entered the room.'}, room=room)


@socket_io.on('text', namespace='/chat')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    emit('message', {'msg': session.get('name') + ':' + message['msg']}, room=room)


@socket_io.on('left', namespace='/chat')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    emit('status', {'msg': session.get('name') + ' has left the room.'}, room=room)


@socket_io.on('fetch_me', namespace=our_namespace)
def fetch_all(message):
    print("here i am printing requiest id", request.sid, request.namespace)
    print(message)
    print(datetime.now())
    emit('fetch', {'msg': "HERE IT IS TABLE      " + str(np.random.randint(100))}, )


@socket_io.on('rest_with_id', namespace=our_namespace)
def fetch_rest_object(message):
    rest_json = return_restaurant(message)
    emit('restaurant_object', rest_json)
    return rest_json


@socket_io.on('connect', namespace=our_namespace)
@jwt_required
def connect():
    print('connected')
    print(request.args)
    username = get_jwt_identity()
    print(username)
    previous_sid = AppUser.objects(username=username).first().sid
    if previous_sid:
        print("I have it here", previous_sid)
        disconnect(previous_sid)
    AppUser.objects(username=username).first().update(set__sid=request.sid)
    if AppUser.objects(username=username).first().room == "kids_room":
        join_room("kids_room")
    else:
        join_room("adults_room")
    # all_clients.append(request.sid)


@socket_io.on('shake_hands', namespace=our_namespace)
def shake_hands(message):
    print(message)


@socket_io.on('disconnect', namespace=our_namespace)
def on_disconnect():
    print("Disconnected :( from ", request.sid)


@socket_io.on('fetch_handshake', namespace=our_namespace)
def hand_shake_fetch(message):
    print("here i am printingi requiest id", request.sid, request.namespace)
    print(all_clients)
    global active_clients
    socket_io.emit('hand_shake', active_clients, namespace=our_namespace)
    active_clients = []
    thr = threading.Thread(target=hand_shake_check, args=(), kwargs={})
    thr.start()  # Will run "foo"
    print(threading.active_count())
    print(message)
    print(datetime.now())
    emit('fetch', {'msg': "HERE IT IS TABLE      " + str(np.random.randint(100))}, )


@socket_io.on('hand_shook', namespace=our_namespace)
def hand_shook(message):
    active_clients.append(request.sid)
    print("got ti back from ", request.sid)


def hand_shake_check():
    time.sleep(5)
    for client in all_clients:
        if client in active_clients:
            continue
        with main.test_request_context('/'):
            disconnect(client, namespace=our_namespace)
    return
