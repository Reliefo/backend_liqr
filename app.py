# flask_web/app.py

from flask import Flask,jsonify, request, send_from_directory, url_for
app = Flask(__name__)
import pickle

@app.route('/')
def hello_world():
    return 'Hey, we have Flask in a Docker container!'
@app.route('/menu')
def fetch_menu():
    str_menu = pickle.load(open('half_menu_main.pkl','rb'))
    return str_menu.to_json()


@app.route('/order', methods=['POST'])
def receive_order():
    print(request)
    content = request.json
    print(content)
    return "Fuck yeah buddy"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port="5050")

