from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required, logout_user
from os import path, walk
from flask_cognito import CognitoAuth
from warrant import Cognito
from backend.mongo.query import AppUser, PhoneUser, datetime
import sys

socket_io = SocketIO(logger=True, engineio_logger=False, ping_timeout=10, ping_interval=5, cors_allowed_origins="*")
our_namespace = '/reliefo'
login_manager = LoginManager()

# cogauth = ''

app = Flask(__name__)


@login_manager.request_loader
def load_user_from_request_header(request):
    try:
        access_token = request.headers.get("X-LiQR-Authorization")
        id_token = request.headers.get("X-LiQR-ID")
        unique_id = request.form['unique_id']
        name = request.form['name']

        # sys.stderr.write("LiQR_Error: " + access_token+ " who is a " + str(request.args) + " connected\n")
        cognito = Cognito("ap-south-1_v9uz3gNH6", "2oauo7q0odvn3c99dsevmstk54", user_pool_region="ap-south-1",
                          access_token=access_token, id_token=id_token)
        username = cognito.get_user().sub
        phone_number = cognito.get_user().phone_number
        # sys.stderr.write("LiQR_Error: " + phone_number + " who is a " + " connected\n")
        # sys.stderr.write("LiQR_Error: " + username + " who is a " + " connected\n")
        # sys.stderr.write("LiQR_Error: " + unique_id + " who is a " + " connected\n")
        if len(AppUser.objects(username=username)) == 0:
            print("New user here")
            the_user = PhoneUser(phone_no=phone_number, unique_id=unique_id, name=name, aws_id=username).save()
            app_user = AppUser(username=username, user_type="neo_customer",
                               rest_user=the_user.to_dbref(), timestamp=datetime.now()).save()
            return app_user
        if username is None:
            return None
        print("Old user")
        return AppUser.objects(username=username).first()
    except Exception as e:
        print(e)
        return None


def create_app(debug=False):
    """Create an application."""
    extra_dirs = ['templates/', ]
    extra_files = extra_dirs[:]
    for extra_dir in extra_dirs:
        for dirname, dirs, files in walk(extra_dir):
            for filename in files:
                filename = path.join(dirname, filename)
                if path.isfile(filename):
                    extra_files.append(filename)
    app = Flask(__name__, template_folder="templates/")
    CORS(app)
    app.debug = debug
    app.config['SECRET_KEY'] = '69#js32%_d4-!xd$'
    app.config['JWT_TOKEN_LOCATION'] = ['query_string', 'headers']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 15420
    app.config['JWT_SECRET_KEY'] = '42@s3xn%o69^!xd$'
    app.config['PROPAGATE_EXCEPTIONS'] = True

    # app.config['COGNITO_REGION'] = 'ap-south-1'
    # app.config['COGNITO_USERPOOL_ID'] = 'ap-south-1_v9uz3gNH6'

    # optional
    # app.config['COGNITO_APP_CLIENT_ID'] = '6c3hp92sshqjpemgaof7hplup1' # client ID you wish to verify user is authenticated against
    # app.config['COGNITO_CHECK_TOKEN_EXPIRATION'] = False  # disable token expiration checking for testing purposes
    # app.config['COGNITO_JWT_HEADER_NAME'] = 'X-LiQR-Authorization',
    # app.config['COGNITO_JWT_HEADER_PREFIX'] = 'Bearer',

    login_manager.init_app(app)
    jwt = JWTManager(app)
    # global cogauth
    # cogauth = CognitoAuth(app)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    socket_io.init_app(app)
    return app
