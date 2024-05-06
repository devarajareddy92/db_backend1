from flask_restful import Api
from flask import Flask, jsonify
from configDb import mysql_config
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
api = Api(app)
cors = CORS(app)

# connection = mysql.connector.connect(**mysql_config)
# cursor = connection.cursor()

# def fetch_database_names():
#     try:
#         #Connect to MySQL database
#         connection = mysql.connector.connect(**mysql_config)
#         cursor = connection.cursor()
#         cursor.execute("SHOW DATABASES")

#         # Fetch all rows
#         rows = cursor.fetchall()
#         databases = [row[0] for row in rows]

#         cursor.close()
#         connection.close()

#         return databases

#     except mysql.connector.Error as error:
#         print("Error fetching database names:", error)
#         return None

# def get_database_size(database_name):
#     try:
#         connection = mysql.connector.connect(**mysql_config)
#         cursor = connection.cursor()
#         cursor.execute(f"SELECT SUM(data_length + index_length) / 1024 / 1024 AS 'Size (MB)' from information_schema.tables where table_schema= '{database_name}'")

#         # Fetch the size
#         size = cursor.fetchone()[0]

#         cursor.close()
#         connection.close()

#         return size

#     except mysql.connector.Error as error:
#         print("Error fetching database size:", error)
#         return None


# ----------------------------------------


            

# def get_mysql_version():
#     try:
#         # Connect to MySQL database
#         connection = mysql.connector.connect(**mysql_config)
#         cursor = connection.cursor()

#         # Execute MySQL command to get version
#         cursor.execute("SELECT VERSION()")
#         version = cursor.fetchone()[0]

#         # Close cursor and database connection
#         cursor.close()
#         connection.close()

#         return version
#     except mysql.connector.Error as error:
#         print("Error fetching MySQL version:", error)
#         return None
         
            
# if __name__ == "__main__":
#    app.run(debug=True, host="0.0.0.0",port= "8086")