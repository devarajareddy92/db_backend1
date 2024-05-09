from datetime import datetime, timedelta
from functools import wraps
import json
import os
import socket
import subprocess
from flask import Flask, abort, jsonify, render_template, redirect, request, session
from flask_restful import Api, Resource
from flask_session import Session
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
import jwt
from sqlalchemy import create_engine
import db_info
from configDb import mysql_config
import mysql.connector
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, get_jwt, get_jwt_identity, jwt_required, set_access_cookies, verify_jwt_in_request
from group import create_linux_group
from models import  db, blackList
from database_methods import DatabaseInfo
from api_resources import Api_resources, MysqlStatus
import time
import psutil
from flask_socketio import SocketIO, emit, join_room,send,leave_room

from users import User, create_linux_user
# from flask_migrate import Migrate

app = Flask(__name__)
api = Api(app)

#-----------------------Db configuration--------------------------------
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@host:port/db_name'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://dbadmin:Nsdl$12345@10.101.104.110:3306/db_frontend'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
# f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/"
DB_URL = f"mysql://dbadmin:Nsdl$12345@10.101.104.110:3306/"
# Initialize the SQLAlchemy instance with your Flask app
db.init_app(app)
# db= SQLAlchemy(app)
# migrate=Migrate(app,db)

app.config["SESSION_PERMANENT"] = True
app.secret_key = 'superjsghlt_366key'
app.config["SESSION_TYPE"] = "filesystem"
app.config["JWT-SECRET-KEY"] = "grlkgjrjhikmdkjurgjbwiqfoleergeroguebkbvk"
secret_key = "grlkgjrjhikmdkjurgjbwiqfoleergeroguebkbvk"
app.permanent_session_lifetime = timedelta(seconds=30)  # Set session timeout to 5 minutes
Session(app)
cors=CORS(app)


# def authenticate(username, password):
#     # you should find user in db here
#     # you can see example in docs
#     user = None
#     if user:
#         # do something
#         return user

# def identity(payload):
#     # custom processing. the same as authenticate. see example in docs
#     user_id = payload['identity']
#     return None
# # here what you need
jwt = JWTManager(app)

#--------------------------socket config------------------------------------
# socketio = SocketIO(app)
socketio = SocketIO(app, cors_allowed_origins="http://localhost:5173")
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('join_room')
def user_join_room():
    join_room("graph")
    print("CLient joined the room")

@socketio.on('leave_room')
def user_leave_rooom():
    leave_room("graph") 

def cpu_utilization():
    while True:
        cpu_per = psutil.cpu_percent(interval=1)
        print(cpu_per)
        socketio.emit('message', {'cpu_percent': cpu_per},room="graph")
        time.sleep(1)
         

# Create the tables based on the defined models
with app.app_context():
    db.create_all()

@app.before_request
def check_session_expiry():
    if request.path == "/" and session.get("is_login"):
        last_activity_time = session.get("last_activity_time")
        if last_activity_time is not None:
            # Check if the session has expired based on the last activity time
            if datetime.now() - last_activity_time > timedelta(seconds=30):
                session.clear()  # Expire session if no activity after 30 seconds
                return redirect("/login")
        # Update the last activity time for each request on the index page
        session["last_activity_time"] = datetime.now()

@app.route("/" ,methods=["GET"])
def index():
    if not session.get("is_login"):
        return redirect("/login")
    username = session.get("username")
    check_session_expiry()
    return render_template('index.html', username=username)

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims["is_administrator"]:
                return fn(*args, **kwargs)
            else:
                return jsonify(msg="Admins only!"), 403
        return decorator
    return wrapper


@app.route("/login", methods=["POST"])
def login():
    resJson = request.json
    data = list(resJson.values()) 
    username = data[0].strip()
    password = data[1].strip()
    if data:
        if  username == "deepaks" and password == "password":
            session["username"] = data[0].strip()
            session["is_login"] = True
            session["last_activity_time"] = datetime.now()

            response = jsonify({"msg": "login successful"})
            
            sudo_users_output = subprocess.check_output(['getent', 'group', 'sudo']).decode('utf-8')
            sudo_users = sudo_users_output.split(':')[3].strip().split(',')


            if username in sudo_users:
                role = 'admin'
            else:
                role = 'non-admin'

            if data[0] in sudo_users:
                # Create JWT access token
                access_token = create_access_token(identity=f"{data[0]}", additional_claims={"is_administrator": True, "role":role})
                print(access_token)
                # refresh_token will be used when user didn't logout but its jwt token expired it will refresh token on regular basis
                # refresh_token = create_refresh_token(identity=f"{data[0]}")
                # Set the JWT token in cookies
                set_access_cookies(response, access_token)
                
                response_data = {
                    "msg": "login successful",
                    "token": access_token
                }
            
                return jsonify(response_data)
            else:
                return jsonify({"message": "User is not authorized"}), 403
        else:
            return jsonify({"message": "Username or password incorrect"}), 401
    else:
        return jsonify({"message": "No data received"}), 400

# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     username = data.get('username')
#     password = data.get('password')

#     # Example command for authentication, replace with your actual authentication command
#     command = ['authentication_script.py', username, password]

#     try:
#         result = subprocess.run(command, capture_output=True, text=True, check=True)
#         if result.stdout.strip() == 'authenticated':
#             return jsonify({'message': 'Login successful'}), 200
#         else:
#             return jsonify({'message': 'Invalid credentials'}), 401
#     except subprocess.CalledProcessError:
#         return jsonify({'message': 'Error during authentication'}), 500
    
# def check_sudo_rights(username):
#     process = subprocess.Popen(['sudo', '-l', '-U', username], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     out, err = process.communicate()
#     return process.returncode == 0

class DbInfo(Resource):
    # @jwt_required()
    @staticmethod
    def get():
        
        mysql_version = Api_resources.mysqlVersion()[0]
        print(mysql_version)
        #mysql_version = DatabaseInfo.execute_query_one("SELECT VERSION();")
        mysql_base_path = DatabaseInfo.execute_query_one("SHOW VARIABLES LIKE 'basedir';")
        print(mysql_base_path)
        databases = DatabaseInfo.execute_query_all("SHOW DATABASES;")
        print(databases)
        uptime_seconds = DatabaseInfo.execute_query_one("SHOW GLOBAL STATUS LIKE 'Uptime';")
        print(uptime_seconds)
        datadir = DatabaseInfo.execute_query_one("SHOW VARIABLES LIKE 'datadir';")
        print(datadir)
        db_size = Api_resources.dbSize()
        print(db_size)
        mysql_status = MysqlStatus.mysql_status()
        print(mysql_status)
        return jsonify({
            'mysql_version': mysql_version[0],
            'mysql_base_path': mysql_base_path[1],
            'databases': [db[0] for db in databases],
            'uptime_seconds': uptime_seconds[1],
            'mysql_data_path': datadir[1],
            'mysql_status': mysql_status,
            'databases_size': db_size
        })
api.add_resource(DbInfo, '/db_info')

class SlowQuery(Resource):
    def analyze_slow_query_log(self, mysql_config):
        connection = None
        try:
            connection = mysql.connector.connect(**mysql_config)

            with connection.cursor() as cursor:
                # Analyze slow query log
                cursor.execute("SHOW VARIABLES LIKE 'slow_query_log';")
                slow_query_log_status = cursor.fetchone()[1]
                if slow_query_log_status != 'ON':
                    return "Slow query log is not enabled."

                cursor.execute("SHOW VARIABLES LIKE 'long_query_time';")
                long_query_time = cursor.fetchone()[1]

                cursor.execute("SHOW VARIABLES LIKE 'slow_query_log_file';")
                slow_query_log_file = cursor.fetchone()[1]

                # Use absolute file path
                slow_query_log_file_path = os.path.abspath(slow_query_log_file)

                # Read slow query log file
                with open(slow_query_log_file_path, 'r') as log_file:
                    slow_queries = log_file.readlines()
                    result = {
                        "long_query_time_threshold": long_query_time,
                        "slow_query_log_file": slow_query_log_file,
                        "slow_queries": slow_queries
                    }
                    return result

        except mysql.connector.Error as e:
            return f"Error: {e}"
        finally:
            if connection:
                connection.close()

    def get(self):
        result = self.analyze_slow_query_log(mysql_config)
        return jsonify(result)

api.add_resource(SlowQuery, '/slow_queries')

def check_user_detail(jwt_token, fun_val):
    #role find 
    #function_name
    #app_code= createdb
    try:
        decoded_token = jwt.decode(jwt_token, secret_key, algorithms=['HS256'])
        role = decoded_token.get('role')
        engine = create_engine(DB_URL)

        connection = engine.connect()
        role_key_result = connection.execute(f"SELECT role_key FROM db_user_key WHERE role_name = '{role}'")
        role_key = role_key_result.fetchone()[0] if role_key_result else None

        # Find the function_key for the given function_name
        funct_key_result = connection.execute(f"SELECT function_key FROM db_function WHERE function_name = '{fun_val}'")
        funct_key = funct_key_result.fetchone()[0] if funct_key_result else None

        if role_key and funct_key:
            # Check if there is a mapping for the role_key and function_key
            function_count_result = connection.execute(f"SELECT COUNT(*) AS function_count FROM db_role_key WHERE role_key = '{role_key}' AND function_key = '{funct_key}'")
            function_count = function_count_result.fetchone()[0] if function_count_result else 0

            connection.close()

            if function_count > 0:
                return True  
            else:
                return False  
        else:
            connection.close()
            return False  # Role or function not found

    except Exception as e:
        return str(e)  # Return error message if any exception occurs

# @app.route('/insert_user_info', methods=['POST'])
# def insert_user_info():
#     try:
#         # Retrieve user information using getent command
#         user_info = subprocess.check_output(['getent', 'passwd']).decode('utf-8')

#         # Parse user information and insert into the database
#         for line in user_info.splitlines():
#             username, _, _, _, _, groupname, _ = line.split(':')
#             users_group = User(username=username, groupname=groupname)
#             session.add(users_group)

#         # Commit the changes
#         session.commit()

#         return jsonify({"message": "User information has been successfully inserted into the database."}), 200

#     except subprocess.CalledProcessError as e:
#         return jsonify({"error": f"Error executing getent command: {e}"}), 500

#     except Exception as e:
#         return jsonify({"error": f"An error occurred: {e}"}), 500

#-----------------------API to create database----------------------------------------
@app.route('/create_database', methods=['POST'])
def create_database():
    # if check_user_detail:
        try:
            data = request.get_json()  # Call get_json() method to retrieve JSON data
            db_name = data.get('db_name')

            # If db_name is not provided in the request
            if not db_name:
                return jsonify({"error": "Please provide a database name"}), 400
            
            result = DatabaseInfo.execute_query_one(f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{db_name}'")
            
            print(result)
            if result:
                return jsonify({"message": f"Database '{db_name}' already exists"}), 200
            DatabaseInfo.execute_query_one(f"CREATE DATABASE {db_name}")

            return jsonify({"message": f"Database '{db_name}' created successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500


#---------------------------OS user creation api-------------------------

@app.route('/create_os_user', methods=['POST'])
def create_user():
    try:
        # Parse the JSON request data
        data = request.json
        username = data.get('username')
        password = data.get('password')

        # Call the create_linux_user method from users module
        response, status_code = create_linux_user(username, password)
        
        return jsonify(response), status_code

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
    
#----------------------Create group at os lebel----------------------
@app.route('/create_group', methods=['POST'])
def create_group():
    data = request.json
    group_name = data.get('group_name')

    if not group_name:
        return jsonify({'error': 'Group name is required'}), 400

    success, message = create_linux_group(group_name)

    if success:
        return jsonify({'message': message}), 200
    else:
        # Provide a user-friendly error message based on the specific error
        if 'non-zero exit status 3' in message:
            return jsonify({'error': 'Failed to create group. Please check if the group name is valid and unique.'}), 500
        else:
            return jsonify({'error': 'An error occurred while creating the group. Please try again later.'}), 500
    

#-----------------------database Info---------------------------------

@app.route('/list_db', methods=['GET'])
def get_database_info():
    try:
        # Call dbSize() to get database sizes
        databases_size = Api_resources.dbSize()

        # Call get_creation_date() to get creation dates
        creation_date = Api_resources.get_creation_date()

        # Call get_db_engine() to get database engines
        db_engine = Api_resources.get_db_engine()

        # Prepare the response
        response_data = {
            "databases_size": databases_size,
            "creation_date": creation_date,
            "db_engine": db_engine
        }

        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
# while True:
#     cpu_per = psutil.cpu_percent(interval=1)
#     socketio.emit('message', {'cpu_percent': cpu_percent},room="graph")
#     time.sleep(1)


@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    # Add token's JTI to the blacklist in the database
    jti = jwt.get_raw_jwt()['jti']
    token = blackList(jti=jti, revoked_at=datetime.utcnow())
    db.session.add(token)
    db.session.commit()
    response = jsonify({"msg": "logout successful"})
    return response

@app.route('/protected')
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# Token revocation callback
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_data):
    jti = jwt_data['jti']
    return blackList.query.filter_by(jti=jti).first() is not None


def get_cpu_utilization():
    cpu_percent = psutil.cpu_percent(interval=1)
    return cpu_percent

# Function to send data over socket
def send_data(data):
    HOST = '127.0.0.1'  # Server IP address
    PORT = 65432        # Port to listen on

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(json.dumps(data).encode())


# @app.route("/get_my_ip", methods=["GET"])
# def get_my_ip():
#     return jsonify({'ip': request.environ['REMOTE_ADDR']}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0",port= "8087")
    socketio.run(app)
    try:
        while True:
            cpu_utilization = get_cpu_utilization()
            data = {'cpu_utilization': cpu_utilization}
            print("CPU Utilization:", cpu_utilization)
            send_data(data)
            time.sleep(1)  # Sleep for 1 second before getting CPU utilization again
    except KeyboardInterrupt:
        print("Exiting...")
    
