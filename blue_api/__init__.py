from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required, logout_user
from os import path, walk
from flask_cognito import CognitoAuth
from warrant import Cognito
from backend.mongo.query import AppUser

socket_io = SocketIO(logger=True, engineio_logger=False, ping_timeout=10, ping_interval=5, cors_allowed_origins="*")
our_namespace = '/reliefo'
login_manager = LoginManager()

cogauth = ''


app = Flask(__name__)


@login_manager.request_loader
def load_user_from_request_header(request):
    try:
        access_token = request.headers["X-LiQR-Authorization"]
        cognito = Cognito("ap-south-1_rO5dDlChJ", "6c3hp92sshqjpemgaof7hplup1", access_token)
        username = cognito.get_user()._metadata.get("username")
        if username is None:
            return None
        return AppUser.objects(username=username)
    except Exception as e:
        return None


def create_app(debug=False):
    """Create an application."""
    extra_dirs = ['templates/',]
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

    app.config['COGNITO_REGION'] = 'ap-south-1'
    app.config['COGNITO_USERPOOL_ID'] = 'ap-south-1_rO5dDlChJ'

    # optional
    # app.config['COGNITO_APP_CLIENT_ID'] = '6c3hp92sshqjpemgaof7hplup1' # client ID you wish to verify user is authenticated against
    app.config['COGNITO_CHECK_TOKEN_EXPIRATION'] = False  # disable token expiration checking for testing purposes
    app.config['COGNITO_JWT_HEADER_NAME'] = 'X-LiQR-Authorization',
    app.config['COGNITO_JWT_HEADER_PREFIX'] = 'Bearer',

    login_manager.init_app(app)
    # jwt = JWTManager(app)
    # global cogauth
    # cogauth = CognitoAuth(app)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    socket_io.init_app(app)
    return app
