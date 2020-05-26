from flask import session, jsonify, request
from backend.mongo.mongodb import *
from backend.mongo.query import user_scan
from backend.mongo.utils import str_n
import sys
import re
from flask_login import current_user, login_user, login_required, logout_user
from . import main
from .. import socket_io, our_namespace, login_manager
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import (
    get_jwt_identity, jwt_required, create_access_token, create_refresh_token, jwt_refresh_token_required
)
from backend.aws_api.sns_registration import update_staff_endpoint


@login_manager.user_loader
def load_user(user_id):
    return AppUser.objects.get(id=user_id)


@main.route('/user_register', methods=['POST'])
def user_register():
    if request.method == 'POST':
        unique_id = request.form['unique_id']
        email_id = request.form['email_id']
        name = request.form['name']
        table_id = request.form['table_id']
        restaurant_object = Restaurant.objects.filter(tables__in=[table_id]).first()
        hash_pass = generate_password_hash(request.form["password"], method='sha256')
        if len(User.objects(email_id=email_id)) > 0:
            return json_util.dumps({"status": "User alreadt registered"})
        if re.search("\$", unique_id):
            tempuser_ob = TempUser.objects(unique_id=unique_id).first()
            reguser_ob = RegisteredUser(name=name, email_id=email_id, tempuser_ob=str(tempuser_ob.id))
            reguser_ob.dine_in_history = tempuser_ob.dine_in_history
            reguser_ob.save()
            tempuser_ob.reguser_ob = str(reguser_ob.id)
            tempuser_ob.save()
            the_user = user_scan(table_id, unique_id, email_id)
            app_user = AppUser.objects(rest_user__in=[tempuser_ob.id]).first()
            app_user.rest_user = reguser_ob.to_dbref()
            app_user.password = hash_pass
            app_user.save()
        else:
            reguser_ob = RegisteredUser(name=name, email_id=email_id)
            reguser_ob.save()
            the_user = user_scan(table_id, unique_id, email_id)
            existing_no = len(AppUser.objects(user_type__in=['customer']))
            username = "CID" + str_n(existing_no + 1, 6)
            app_user = AppUser(username=username, password=hash_pass, room="cust_room",
                               rest_user=reguser_ob.to_dbref()).save()
            login_user(app_user)

        socket_io.emit('user_scan', the_user.to_json(), room=restaurant_object.manager_room, namespace=our_namespace)
        access_token = create_access_token(identity=app_user["username"])
        refresh_token = create_refresh_token(identity=app_user["username"])
        return json_util.dumps(
            {"status": "Registration successful", "jwt": access_token, "refresh_token": refresh_token, "code": "200",
             "name": the_user.name, "email": the_user.email_id, "user_id": str(the_user.id),
             "restaurant_id": restaurant_object.restaurant_id})
    return json_util.dumps({"status": "Registration failed"})


@main.route('/user_login', methods=['POST'])
def user_login():
    if request.method == 'POST':
        unique_id = request.form['unique_id']
        email_id = request.form['email_id']
        password = request.form['password']
        table_id = request.form['table_id']
        restaurant_object = Restaurant.objects.filter(tables__in=[table_id])[0]
        if re.search("\$", unique_id) and len(User.objects.filter(unique_id=unique_id)) > 0:
            if email_id == "dud":
                the_user = user_scan(table_id, unique_id)
                check_user = AppUser.objects(rest_user__in=[the_user.id]).first()
                password = "temp_pass" + check_user['username']
            else:
                the_user = user_scan(table_id, unique_id, email_id)
        else:
            if re.search("\$", unique_id):
                unique_id = unique_id.split("$")[0]
            if email_id == "dud":
                the_user = user_scan(table_id, unique_id)
                existing_no = len(AppUser.objects(user_type__in=['customer']))
                username = "CID" + str_n(existing_no + 1, 6)
                password = "temp_pass" + username
                hash_pass = generate_password_hash("temp_pass" + username, method='sha256')
                AppUser(username=username, user_type="customer", room="cust_room", password=hash_pass,
                        rest_user=the_user.to_dbref(), timestamp=datetime.now()).save()
            else:
                the_user = user_scan(table_id, unique_id, email_id)
        check_user = AppUser.objects(rest_user__in=[the_user.id]).first()
        if check_user:
            if check_password_hash(check_user['password'], password):
                login_user(check_user)
                socket_io.emit('user_scan', the_user.to_json(), room=restaurant_object.manager_room,
                               namespace=our_namespace)
                access_token = create_access_token(identity=check_user["username"])
                refresh_token = create_refresh_token(identity=check_user["username"])
                if the_user._cls == "User.RegisteredUser":
                    return json_util.dumps(
                        {"status": "Login Success", "jwt": access_token, "refresh_token": refresh_token, "code": "200",
                         "name": the_user.name, "unique_id": the_user.email_id, "user_id": str(the_user.id),
                         "restaurant_id": restaurant_object.restaurant_id})
                else:
                    return json_util.dumps(
                        {"status": "Login Success", "jwt": access_token, "refresh_token": refresh_token, "code": "200",
                         "name": the_user.name, "unique_id": the_user.unique_id, "user_id": str(the_user.id),
                         "restaurant_id": restaurant_object.restaurant_id})

            else:
                return json_util.dumps({"status": "Wrong Password", "code": "401"})
        else:
            return json_util.dumps({"status": "User doesn't exist", "code": "401"})
    return json_util.dumps({"status": "Authentication Failed", "code": "401"})


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        check_user = AppUser.objects(username=request.form["admin_username"]).first()
        if check_user:
            if check_user.user_type == 'admin':
                if check_password_hash(check_user['password'], request.form["admin_password"]):
                    if AppUser.objects.filter(username=request.form["username"]):
                        return json_util.dumps({"status": "Already Registered"})
                    hash_pass = generate_password_hash(request.form["password"], method='sha256')
                    if request.form['user_type'] == "manager":
                        if request.form['new_rest'] == 'yes':
                            if len(Restaurant.objects(restaurant_id=request.form['restaurant_id'])) > 0:
                                return json_util.dumps({"status": "Registration failed, this restaurant already exists"})
                            restaurant_object = Restaurant(name=request.form['restaurant_name'],
                                                           restaurant_id=request.form['restaurant_id'],
                                                           ).save()
                        else:
                            restaurant_object = Restaurant.objects(restaurant_id=request.form['restaurant_id']).first()
                        AppUser(username=request.form["username"], password=hash_pass, timestamp=datetime.now(),
                                manager_name=request.form['manager_name'],
                                restaurant_id=restaurant_object.restaurant_id,
                                user_type=request.form["user_type"]).save()
                        return json_util.dumps({"status": "Registration successful"})

                    AppUser(username=request.form["username"], password=hash_pass, timestamp=datetime.now(),
                            restaurant_id=request.form["restaurant_id"], user_type=request.form["user_type"]).save()
                    return json_util.dumps({"status": "Registration successful"})
                return json_util.dumps({"status": "Registration failed, admin credentials wrong"})
            return json_util.dumps({"status": "User is not admin"})
        return json_util.dumps({"status": "Admin username doesn't exist'"})
    return json_util.dumps({"status": "Registration failed"})


@main.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        check_user = AppUser.objects(username=request.form["username"]).first()
        if check_user:
            if check_user.temp_password:
                if check_password_hash(check_user['password'], request.form["password"]):
                    return json_util.dumps({"status": "Authentication Success, change temporary password"}), 201
                else:
                    return json_util.dumps({"status": "Authentication Failed, wrong temp password"}), 403

            elif check_password_hash(check_user['password'], request.form["password"]):
                if request.form['app'] != check_user.user_type:
                    return json_util.dumps(
                        {"status": "Wrong app. The username and the application you're using don't match"}), 405
                access_token = create_access_token(identity=request.form["username"])
                refresh_token = create_refresh_token(identity=request.form["username"])
                if check_user.user_type == "staff":
                    device_token = request.form['device_token']
                    update_staff_endpoint(device_token, check_user.staff_user)
                    object_id = str(check_user.staff_user.id)
                elif check_user.user_type == "manager":
                    return json_util.dumps(
                        {"status": "Login Success", "jwt": access_token, "refresh_token": refresh_token,
                         "restaurant_id": check_user.restaurant_id, "manager_name": check_user.manager_name}), 200

                elif check_user.user_type == "kitchen":
                    object_id = str(check_user.kitchen_staff.id)
                else:
                    object_id = "nto shiths fas"
                return json_util.dumps(
                    {"status": "Login Success", "jwt": access_token, "refresh_token": refresh_token,
                     "object_id": object_id, "restaurant_id": check_user.restaurant_id}), 200
    return json_util.dumps({"status": "Authentication Failed"}), 403


@main.route('/change_password', methods=['POST'])
def change_password():
    if request.method == 'POST':
        check_user = AppUser.objects(username=request.form["username"]).first()
        if check_user:
            if check_password_hash(check_user['password'], request.form["old_password"]):
                hash_pass = generate_password_hash(request.form["new_password"], method='sha256')
                check_user.password = hash_pass
                check_user.temp_password = False
                check_user.save()
                return json_util.dumps({"status": "Password changed successfully"}), 200
            return json_util.dumps({"status": "Authentication Failed, wrong old password"}), 201
        return json_util.dumps({"status": "Authentication Failed, User doesn't exist"}), 401
    return json_util.dumps({"status": "Authentication Failed, bad request"}), 403


@main.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    device_token = request.form['device_token']
    current_username = get_jwt_identity()
    sys.stderr.write("LiQR_Error: "+current_username+" who has a "+device_token+" connected\n")
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
