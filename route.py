
import os
import sys
import time

import webbrowser
import config 
from utils import db

from flask_migrate import Migrate
from gevent.pywsgi import WSGIServer
from flask import Flask, request, jsonify, make_response
from flask_cors import cross_origin, CORS
from requests import post, get


from server_pile import Server
from utils import Authorization, Time

import json
from user_bill import User

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config.from_object(config)
db.init_app(app)

migrate = Migrate(app, db)

@app.route('/')
@cross_origin()
def index():
    return app.send_static_file('index.html')

@app.route('/<path:fallback>')
@cross_origin()
def fallback(fallback):
    if fallback.startswith('css/') or fallback.startswith('js/') or fallback == 'favicon.ico':
        return app.send_static_file(fallback)

# ---------- User Controller ----------


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


@app.route('/user/register/', methods=['POST', 'GET'])
@cross_origin()
def router_user_register():
    id = request.json['id']
    password = request.json['password']
    is_admin = request.json['is_admin']
    auth = Authorization(id, password, is_admin)
    result = auth.register()
    response = make_response()
    if result:
        response.status_code = 200
    else:
        response.status_code = 400
    return response


@app.route('/request/', methods=['POST', 'GET'])
@cross_origin()
def router_request():
    id = request.json['id']
    charge_volume = request.json['charge_volume']
    fast_charge = request.json['fast_charge']
    server.schedule()
    if not server.find_charge_user(id):
        server.queue_number+=1
        user = User(id, server.queue_number, 0 if fast_charge else 1, charge_volume, server.timer.get_time_sec())
        server.waiting_queue[0 if fast_charge else 1].append(user)
        response = make_response("successfully request")
        response.status_code = 200
        return response
    response = make_response("The car_id was appeared before.")
    response.status_code = 400
    return response
    
    
@app.route('/request/modify/', methods=['POST', 'GET'])
@cross_origin()
def router_request_modify():
    id = request.json['id']
    charge_volume = request.json['charge_volume']
    type_choice = request.json['type_choice']
    server.schedule()
    if server.find_charge_user(id):
        server.modify_mode(id, type_choice, charge_volume)
        response = make_response("successfully modify")
        response.status_code = 200
        return response
    response = make_response("The car_id was not appeared before.")
    response.status_code = 400
    return response
    
    
@app.route('/request/end/', methods=['POST', 'GET'])
@cross_origin()
def router_request_end():
    id = request.json['id']
    server.schedule()
    if not server.find_priority_user(id, True):
        if not server.find_waiting_user(id, True):
            if not server.find_charge_user(id, True):
                response = make_response("The car_id was not appeared before.")
                response.status_code = 400
            else:
                response = make_response("successfully end")
                response.status_code = 200
        else:
            response = make_response("successfully end")
            response.status_code = 200
    else:
        response = make_response("successfully end")
        response.status_code = 200
    
    server.schedule()
    
    return response
    
    
@app.route('/user/info/', methods=['POST', 'GET'])
@cross_origin()
def router_user_info():
    id = request.args['id']
    print('user_info_begin')
    server.schedule()
    print('user_info_end')
    bill = server.query_user_bill(id)
    t1, tfront = server.get_priority_queue_number(id)
    if t1 == -1:
        t2, tfront = server.get_waiting_queue_number(id)
        if t2 == -1:
            t3,t4 = server.get_charge_queue_number(id)
            if t3==-1:
                status = "idle"
                queue_number = -1
                waiting_in_front = -1
            else:
                if t3 == 0 :
                    status = "charging"
                else:
                    status = "ready to charge"
                queue_number = t4
                waiting_in_front = t3
        else:
            status = "queueing"
            queue_number = t2
            waiting_in_front= tfront + len(server.priority_queue)
    else:
        status = "queueing"
        queue_number = t1
        waiting_in_front= tfront
    if bill:
        response = make_response({"bills": bill, "status": status, "queue_number": queue_number, "waiting_in_front": waiting_in_front})
        response.status_code = 200
        return response
    else:
        response = make_response({"bills": bill, "status": status, "queue_number": queue_number, "waiting_in_front": waiting_in_front})
        response.status_code = 400
        return response
    
    
@app.route('/pile/admin/', methods=['POST', 'GET'])
@cross_origin()
def router_pile_admin():
    server.schedule()
    reports = server.query_pile_report()
    time = server.timer.get_time_string()
    response = make_response({"reports": reports, "time": time})
    response.status_code = 200
    return response
    
    
@app.route('/pile/startup/', methods=['POST', 'GET'])
@cross_origin()
def router_pile_startup():
    server.schedule()
    print([i.user_id for i in server.priority_queue[1]])
    pile_id = int(request.json['pile_id'])
    if server.pile[pile_id].status == 0:
        server.recovery(pile_id)
        response = make_response("successfully startup")
        response.status_code = 200
    else:
        response = make_response("The pile has been started up.")
        response.status_code = 400
    return response


@app.route('/pile/shutdown/', methods=['POST', 'GET'])
@cross_origin()
def router_pile_shutdown():
    server.schedule()
    pile_id = int(request.json['pile_id'])
    if server.pile[pile_id].status == 1:
        server.error(pile_id)
        response = make_response("successfully shutdown")
        response.status_code = 200
    else:
        response = make_response("The pile has been shutdown.")
        response.status_code = 400
    return response
    

@app.route('/pile/queue/', methods=['POST', 'GET'])
@cross_origin()
def router_pile_queue():
    server.schedule()
    pile_id = int(request.args['pile_id'])
    print('pile_id : ', pile_id)
    items = server.query_waiting_queue(pile_id)
    response = make_response({"items": items})
    response.status_code = 200
    return response

    
    
if __name__ == '__main__':
    if __debug__:
        print('Debug Mode')
    
    timer = Time()
    server = Server(timer)
    # webbrowser.open('http://localhost:8123')
    app.run(port=8123)
