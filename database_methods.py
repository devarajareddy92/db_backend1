import mysql.connector
from flask_restful import Resource
from configDb import mysql_config

class DatabaseInfo(Resource):
    def execute_query_one(query):
        connection=None
        try:
            connection = mysql.connector.connect(**mysql_config)
            with connection.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchone()
        except mysql.connector.Error as e:
            return str(e)
        finally:
            if connection:
                connection.close()

    def execute_query_all(query):
        connection=None
        try:
            connection = mysql.connector.connect(**mysql_config)
            with connection.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        except mysql.connector.Error as e:
            return str(e)
        finally:
            if connection:
                connection.close()

    @staticmethod
    def execute_insert(query, values):
        connection = None
        try:
            connection = mysql.connector.connect(**mysql_config)
            with connection.cursor() as cursor:
                cursor.execute(query, values)
                connection.commit()
                return cursor.rowcount  # Return the number of affected rows
        except mysql.connector.Error as e:
            return str(e)
        finally:
            if connection:
                connection.close()

    