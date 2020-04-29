from flask import session, jsonify, request
from backend.mongo.mongodb import *
from backend.mongo.query import user_scan
from backend.mongo.utils import str_n
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
        hash_pass = generate_password_hash(request.form["password"], method='sha256')
        assigned_room = "kids_room" if request.form["username"][:2] == "KID" else "adults_room"
        print(request.form["username"], " joined ", assigned_room)
        hey = AppUser(username=request.form["username"], password=hash_pass, room=assigned_room).save()
        login_user(hey)
        return json_util.dumps({"status": "Registration successful"})
    return json_util.dumps({"status": "Registration failed"})


@main.route('/user_login', methods=['POST'])
def user_login():
    if request.method == 'POST':
        print(request.form)
        unique_id = request.form['unique_id']
        email_id = request.form['email_id']
        password = request.form['password']
        if re.search("\$", unique_id):
            if email_id == "dud":
                the_user = user_scan(request.form['table_id'], unique_id)
                check_user = AppUser.objects(rest_user__in=[the_user.id]).first()
                password = "temp_pass" + check_user['username']
            else:
                the_user = user_scan(request.form['table_id'], unique_id, email_id)
        else:
            the_user = user_scan(request.form['table_id'], unique_id)
            existing_no = len(AppUser.objects(user_type__in=['customer']))
            username = "CID" + str_n(existing_no + 1, 6)
            password = "temp_pass" + username
            hash_pass = generate_password_hash("temp_pass" + username, method='sha256')
            AppUser(username=username, user_type="customer", room="cust_room", password=hash_pass,
                    rest_user=the_user.to_dbref()).save()
        check_user = AppUser.objects(rest_user__in=[the_user.id]).first()
        if check_user:
            if check_password_hash(check_user['password'], password):
                login_user(check_user)
                access_token = create_access_token(identity=check_user["username"])
                refresh_token = create_refresh_token(identity=check_user["username"])
                return json_util.dumps(
                    {"status": "Login Success", "jwt": access_token, "refresh_token": refresh_token, "code": "200",
                     "name": the_user.name, "unique_id": the_user.unique_id})
            else:
                return json_util.dumps({"status": "Wrong Password", "code": "401"})
        else:
            return json_util.dumps({"status": "User doesn't exist", "code": "401"})
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
