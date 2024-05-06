from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure your database connection URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://dbadmin:Nsdl@12345%@localhost:3306/db_frontend'
db = SQLAlchemy(app)

# to store users details
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)

# to store JWT tokens
class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)

class UserDetail(db.Model):
    __tablename__ = 'user_detail'  

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(255))
    role = db.Column(db.String(255))
    activity = db.Column(db.String(255))
    timestamp = db.Column(db.TIMESTAMP)
    status = db.Column(db.String(255))

class RoleDetail(db.Model):
    __tablename__ = 'role_detail'  

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(255))
    role_description = db.Column(db.String(255))
    function_name = db.Column(db.String(255))
    status = db.Column(db.String(255))
    created_by = db.Column(db.String(255))
    created_timestamp = db.Column(db.TIMESTAMP)
    modified_by = db.Column(db.String(255))
    modified_timestamp = db.Column(db.TIMESTAMP)


class FunctionDetail(db.Model):
    __tablename__ = 'function_detail'  
    
    id = db.Column(db.Integer, primary_key=True)
    function_name = db.Column(db.String(255))
    function_description = db.Column(db.String(255))
    status = db.Column(db.String(255))
    created_by = db.Column(db.String(255))
    created_timestamp = db.Column(db.TIMESTAMP)
    modified_by = db.Column(db.String(255))
    modified_timestamp = db.Column(db.TIMESTAMP)

class role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True)
    function_name = db.Column(db.String(255), nullable=False)
    admin = db.Column(db.Boolean, nullable=False)
    non_admin = db.Column(db.Boolean, nullable=False)
    backup = db.Column(db.Boolean, nullable=False)

# table to store functions available for user
class db_function(db.Model):
    __tablename__ = 'db_function'
    id = db.Column(db.Integer, primary_key=True)
    function_name = db.Column(db.String(55),nullable=False)
    function_key = db.Column(db.String(55), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
# table to store group roles
class db_role_key(db.Model):
    __tablename__ = 'db_group_key'
    id = db.Column(db.Integer, primary_key=True)
    userType = db.Column(db.String(55), nullable=False)
    role_key = db.Column(db.String(55),nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# role and function mapping
class role_function(db.Model):
    __tablename__ = 'role_function'
    id = db.Column(db.Integer, primary_key=True)
    role_key = db.Column(db.String(55),nullable=False)
    function_key = db.Column(db.String(55), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class blackList(db.Model):
    __tablename__ = 'BlacklistToken'
    id = db.Column(db.Integer)
    jti =  db.Column(db.String(55), primary_key = True)
    revoked_at = db.Column(db.DateTime, default=datetime.utcnow)
    

    def __repr__(self):
        return '<User %r>' % self.username
    
# if __name__ == '__main__':
#     app.run(debug=True)