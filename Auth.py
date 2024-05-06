
from flask_restful import Response
from flask import request
from functools import wraps
import jwt
from app import JWT_SECRETKEY


# a middleware to check whether the user has a token to access the restful API or not. If the token is expired or there is no token found, 
# return an error message.
class Auth:
    def middleware(self, func):
        @wraps(func)
        def decorator():
            token=request.cookies.get('x-auth-token')
            if not token:
                return Response.make(False,'Forbidden access')
            try:
                jwt.decode(token, JWT_SECRETKEY, algorithms='HS256')
            except jwt.ExpiredSignatureError:
                return Response.make(False, 'Unauthorized')
            except jwt.InvalidTokenError:
                return Response.make(False, 'Invalid token')
            return func()
        return decorator