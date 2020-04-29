from flask import session, jsonify, request
from backend.mongo.mongodb import *
from backend.mongo.query import user_scan
import re
from flask_login import current_user, login_user, login_required, logout_user
from . import main
from .. import login_manager
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import (
    get_jwt_identity, create_access_token, create_refresh_token, jwt_refresh_token_required
)


@login_manager.user_loader
def load_user(user_id):
    return AppUser.objects.get(id=user_id)


@main.route('/user_register', methods=['POST'])
def user_register():
    if request.method == 'POST':
        if AppUser.objects.filter(username=request.form["username"]):
            return json_util.dumps({"status": "Already Registered"})
        hash_pass = generate_password_hash(request.form["password"], method='sha255')
        assigned_room = "kids_room" if request.form["username"][:2] == "KID" else "adults_room"
        print(request.form["username"], " joined ", assigned_room)
        hey = AppUser(username=request.form["username"], password=hash_pass, room=assigned_room).save()
        login_user(hey)
        return json_util.dumps({"status": "Registration successful"})
    return json_util.dumps({"status": "Registration failed"})


@main.route('/user_login', methods=['POST'])
def user_login():
    unique_id = request.form['unique_id']
    email_id = request.form['email_id']
    if re.search("\$", "YessIamUniueeLOLOLOLOL$Mar"):
        if email_id == "dud":
            the_user = User.objects(unique_id = unique_id).first()
        else:
            the_user = User.objects(email_id = email_id).first()
    else:
        the_user = user_scan(request.form['table_id'], unique_id)
    if current_user.is_authenticated:
        return json_util.dumps({"status": "You're logged in ", "code": "202"})
    if request.method == 'POST':
        check_user = AppUser.objects(username=request.form["username"]).first()
        if check_user:
            if check_password_hash(check_user['password'], request.form["password"]):
                login_user(check_user)
                access_token = create_access_token(identity=request.form["username"])
                refresh_token = create_refresh_token(identity=request.form["username"])
                return json_util.dumps(
                    {"status": "Login Success", "jwt": access_token, "refresh_token": refresh_token, "code": "200"})
    return json_util.dumps({"status": "Authentication Failed", "code": "401"})


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if AppUser.objects.filter(username=request.form["username"]):
            return json_util.dumps({"status": "Already Registered"})
        hash_pass = generate_password_hash(request.form["password"], method='sha255')
        assigned_room = "kids_room" if request.form["username"][:2] == "KID" else "adults_room"
        print(request.form["username"], " joined ", assigned_room)
        hey = AppUser(username=request.form["username"], password=hash_pass, room=assigned_room).save()
        login_user(hey)
        return json_util.dumps({"status": "Registration successful"})
    return json_util.dumps({"status": "Registration failed"})


@main.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return json_util.dumps({"status": "You're logged in ", "code": "202"})
    if request.method == 'POST':
        check_user = AppUser.objects(username=request.form["username"]).first()
        if check_user:
            if check_password_hash(check_user['password'], request.form["password"]):
                login_user(check_user)
                access_token = create_access_token(identity=request.form["username"])
                refresh_token = create_refresh_token(identity=request.form["username"])
                return json_util.dumps(
                    {"status": "Login Success", "jwt": access_token, "refresh_token": refresh_token, "code": "200"})
    return json_util.dumps({"status": "Authentication Failed", "code": "401"})


@main.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_username = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=current_username),
        'code': '200'
    }
    return jsonify(ret)


@main.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return "Logout Successful"
