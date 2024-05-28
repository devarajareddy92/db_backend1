from flask import Flask, jsonify
from flask_restful import Api, Resource
import mysql.connector
from database_methods import DatabaseInfo
import subprocess
import os
from configDb import mysql_config

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://dbadmin:Nsdl$12345@10.101.104.110:3306/db_frontend'

# Direct MySQL connection configuration
mysql_config = {
    'host': '10.101.104.110',
    'user': 'dbadmin',
    'password': 'Nsdl$12345',
    'database': 'db_frontend'
}

# class DatabaseInfo(Resource):
#     def execute_query(self, query):
#         try:
#             connection = mysql.connector.connect(**mysql_config)
#             with connection.cursor() as cursor:
#                 cursor.execute(query)
#                 return cursor.fetchone()[1]
#         except mysql.connector.Error as e:
#             return str(e)
#         finally:
#             if connection:
#                 connection.close()

class Api_resources(DatabaseInfo):    
    def get(self):
        return jsonify({'error': 'Method Not Allowed'}), 405
    

# class MysqlVersion(DatabaseInfo):
    def mysqlVersion():
        try:
            version = DatabaseInfo.execute_query_one("SELECT VERSION();")
            return version, 200
        except Exception as e:
            return {'error': str(e)}, 500

# class DbBasePath(DatabaseInfo):
    def baseDir():
        basedir = DatabaseInfo.execute_query_one("SHOW VARIABLES LIKE 'basedir';")
        if isinstance(basedir, str):
            return {'error': basedir}, 500
        return {'mysql_base_path': basedir}, 200

# class ListDb(DatabaseInfo):
    def showDatabases():
        databases = DatabaseInfo.execute_query_all("SHOW DATABASES;")
        if isinstance(databases, str):
            return jsonify({'error': databases}), 500
        return jsonify({'databases': [db for db in databases]}), 200

# class DatabaseSize(DatabaseInfo):
    def dbSize():
        query = """
            SELECT
                table_schema AS `Database`,
                ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS `Size_MB`
            FROM
                information_schema.tables
            GROUP BY
                table_schema;
        """
        databases_size = DatabaseInfo.execute_query_all(query)
        data = {}
        
        for row in databases_size:
            if len(row) >= 2:
                database_name, size_MB = row[:2]  # Ensure at least two values are unpacked
                data[database_name] = size_MB
            else:
                # If the row doesn't contain enough values, skip it or handle it as needed
                pass
        
        if isinstance(data, str):
            return {'error': "size not found"}, 500
        
        return data, 200

# class Uptime(DatabaseInfo):
    def upTime():
        uptime_seconds = DatabaseInfo.execute_query_one("SHOW GLOBAL STATUS LIKE 'Uptime';")
        if isinstance(uptime_seconds, str):
            return jsonify({'error': uptime_seconds}), 500
        return jsonify({'uptime_seconds': uptime_seconds}), 200

# class DbDataPath(DatabaseInfo):
    def dataPath():
        datadir = DatabaseInfo.execute_query_one("SHOW VARIABLES LIKE 'datadir';")
        if isinstance(datadir, str):
            return jsonify({'error': datadir}), 500
        return jsonify({'mysql_data_path': datadir}), 200
    
    def get_creation_date():
        try:
            query = """
            SELECT Database_Name, MIN(Creation_Date) AS Creation_Date
            FROM (
                SELECT DISTINCT TABLE_SCHEMA AS Database_Name, CREATE_TIME AS Creation_Date 
                FROM information_schema.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
            ) AS subquery 
            GROUP BY Database_Name
            """
            results = DatabaseInfo.execute_query_all(query)

            data = {}
            for result in results:
                database_name, creation_date = result
                data[database_name] = creation_date.strftime("%Y-%m-%d %H:%M:%S")
            
            return data, 200
        except Exception as e:
            print(f"Error while fetching creation dates for databases: {e}")
            return None


    def get_db_engine():
        try:
            query = f"SELECT TABLE_SCHEMA AS Database_Name, ENGINE FROM information_schema.TABLES GROUP BY TABLE_SCHEMA, ENGINE"

            results = DatabaseInfo.execute_query_all(query)

            data = {}
            for result in results:
                database_name, engine = result
                data[database_name] = engine
            
            return data, 200
        except Exception as e:
            print(f"Error while fetching creation dates for databases: {e}")
            return None

class MysqlStatus(Resource):
    @staticmethod
    
#To return only the status of the MySQL service (whether it's running or not) from the provided mysql_status data, you can iterate over the list of dictionaries and check the value associated with the key 'mysql.service'. If the value is 'active', then the service is running; otherwise, it's not. Here's how you can modify the mysql_status() function to achieve this:

    def mysql_status():
        try:
            # Use 'systemctl status mysql*' to get the status of MySQL service on Linux
            result = subprocess.check_output(['systemctl', 'status', 'mysql*']).decode()
            lines = [line.strip() for line in result.split("\n") if line.strip()]
            header = lines[0].split()
            data = [line.split(None, len(header) - 1) for line in lines[1:]]
            rows = [dict(zip(header, row)) for row in data]
            
            # Find the dictionary containing the status information
            status_dict = next((row for row in rows if row.get('mysql.service') == 'active'), None)
            
            # Extract and return the status
            if status_dict:
                return status_dict['mysql.service'], 200
            else:
                return 'MySQL service is not running', 200
        except subprocess.CalledProcessError as e:
            return str(e), 500

        
# class SlowQuery(Resource):
#     def analyze_slow_query_log(mysql_config):
#         connection = None
#         try:
#             connection = mysql.connector.connect(**mysql_config)

#             with connection.cursor() as cursor:
#                 # Analyze slow query log
#                 cursor.execute("SHOW VARIABLES LIKE 'slow_query_log';")
#                 slow_query_log_status = cursor.fetchone()[1]
#                 if slow_query_log_status != 'ON':
#                     return "Slow query log is not enabled."

#                 cursor.execute("SHOW VARIABLES LIKE 'long_query_time';")
#                 long_query_time = cursor.fetchone()[1]

#                 cursor.execute("SHOW VARIABLES LIKE 'slow_query_log_file';")
#                 slow_query_log_file = cursor.fetchone()[1]

#                 # Use absolute file path
#                 slow_query_log_file_path = os.path.abspath(slow_query_log_file)

#                 # Read slow query log file
#                 with open(slow_query_log_file_path, 'r') as log_file:
#                     slow_queries = log_file.readlines()
#                     result = {
#                         "long_query_time_threshold": long_query_time,
#                         "slow_query_log_file": slow_query_log_file,
#                         "slow_queries": slow_queries
#                     }
#                     return result

#         except mysql.connector.Error as e:
#             return f"Error: {e}"
#         finally:
#             if connection:
#                 connection.close()




if __name__ == '__main__':
    app.run(debug=True)
    





    
