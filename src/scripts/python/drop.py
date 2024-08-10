from typing import List
import pyodbc
from pyodbc import Cursor
import argparse
import os

parser = argparse.ArgumentParser(description="drop.py")
parser.add_argument("database_name", help="Database Name")
args = parser.parse_args()

server = 'localhost'
database = 'master'
username = 'SA'
password = os.getenv('SA_PASSWORD', 'R00tIkr@') 

connectionString = (
    f'DRIVER={{ODBC Driver 18 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password};'
    f'Encrypt=no;'
    f'TrustServerCertificate=yes;'
)

connection = None

def check_database_exists(cursor: Cursor, database_name: str) -> bool:
    check_query = f"""
    SELECT COUNT(*) 
    FROM sys.databases 
    WHERE name = ?
    """
    cursor.execute(check_query, (database_name,))
    result = cursor.fetchone()
    return result[0] > 0

def drop_database(cursor: Cursor, database_name: str):
    if not check_database_exists(cursor, database_name):
        raise ValueError(f"Database '{database_name}' not found.")
    single_user_query = f"ALTER DATABASE [{database_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE"
    cursor.execute(single_user_query)
    drop_query = f"DROP DATABASE [{database_name}]"
    cursor.execute(drop_query)

    print(f"Databse '{database_name}' was deleted.")

try:
    connection = pyodbc.connect(connectionString)
    connection.autocommit = True
    cursor = connection.cursor()
    drop_database(cursor, args.database_name)
    cursor.close()
except ValueError as ve:
    print(f"Error: {ve}")
except Exception as e:
    print(f"Error: {e}")
finally:
    if connection:
        connection.close()