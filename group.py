import json
from flask import Flask
import subprocess
from database_methods import DatabaseInfo

def create_linux_group(group_name):
    try:
        query1 = "SELECT * FROM db_group_key WHERE group_name = %s"
        result = DatabaseInfo.execute_query_one(query1)
        if result:
                return False, f'Group {group_name} already exists in the database'
        # Load sudo password from config.json
        with open('config.json') as f:
            config = json.load(f)
            sudo_password = config.get('sudo_password')

        # Execute sudo groupadd command with the sudo password
        command = f'echo {sudo_password} | sudo -S groupadd {group_name}'
        subprocess.run(command, shell=True, check=True)
        
        key = "SELECT MAX(role_key) AS max_role_key FROM groups"
        max_role_key_result = DatabaseInfo.execute_query_one(key)
        max_role_key = max_role_key_result['max_role_key'] if max_role_key_result['max_role_key'] else 0
        new_role_key = max_role_key + 1

        query2 = "INSERT INTO db_group_key (group_name, new_role_key) VALUES (%s, %s)"
        values = (query2, new_role_key)
        DatabaseInfo.execute_query_one(query2, values)

        return True, f'Group {group_name} created successfully'
    except subprocess.CalledProcessError as e:
        return False, str(e)