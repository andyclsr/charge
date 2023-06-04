
from flask_migrate import Migrate
from gevent.pywsgi import WSGIServer
from flask import Flask, request, jsonify, make_response
from flask_cors import cross_origin, CORS
from requests import post, get
import config  # sql配置

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config.from_object(config)
db.init_app(app)

@app.route('/user/login/', methods=['POST', 'GET'])
@cross_origin()
def router_user_login():
    id = request.json['id']
    password = request.json['password']
    is_admin = request.json['is_admin']
    auth = Authorization(id, password, is_admin)
    result = auth.login()
    response = make_response()
    if result:
        response.status_code = 200
    else:
        response.status_code = 400
    return response

if __name__ == '__main__':
    
    # ....

    # webbrowser.open('http://localhost:8123')
    app.run(port=8123)