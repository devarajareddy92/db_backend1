import json
from flask import Flask, jsonify, request
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import subprocess

# Initialize Flask app
app = Flask(__name__)

# Create SQLAlchemy engine
engine = create_engine('mysql+mysqlconnector://dbadmin:Nsdl$12345@localhost/db_frontend')

# Define SQLAlchemy base
Base = declarative_base()

# Define User model
class User(Base):
    __tablename__ = 'users_group'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    groupname = Column(String)

# Create tables
Base.metadata.create_all(engine)

# Create a sessionmaker
Session = sessionmaker(bind=engine)

# Define API endpoint to insert Linux user information into the database
@app.route('/insert_user_info', methods=['POST'])
def insert_user_info():
    try:
        # Create a new session
        session = Session()

        # Retrieve user information using getent command
        user_info = subprocess.check_output(['getent', 'passwd']).decode('utf-8')

        # Parse user information and insert into the database
        for line in user_info.splitlines():
            username, _, _, _, _, groupname, _ = line.split(':')
            user = User(username=username, groupname=groupname)
            session.add(user)

        # Commit the changes
        session.commit()

        return jsonify({"message": "User information has been successfully inserted into the database."}), 200

    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Error executing getent command: {e}"}), 500

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

    finally:
        # Close the session
        session.close()

with open('config.json') as config_file:
    config = json.load(config_file)

def create_linux_user(username, password):
    try:
        # Check if both username and password are provided
        if not username or not password:
            return {"error": "Both username and password are required"}, 400

        # Create the user using the 'useradd' command
        subprocess.run(['sudo', 'useradd', '-m', username])

        # Set the password for the user using 'passwd' command
        passwd_process = subprocess.Popen(['sudo', 'passwd', username], stdin=subprocess.PIPE)
        passwd_process.communicate(input=f"{password}\n{password}\n".encode())

        return {"message": f"User '{username}' created successfully"}, 200

    except Exception as e:
        return {"error": f"An error occurred: {e}"}, 500
    

if __name__ == '__main__':
    app.run(debug=True, port=8086)
