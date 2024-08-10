from typing import List
import pyodbc
from pyodbc import Cursor
import argparse
import os
 
parser = argparse.ArgumentParser(description="Restore.py")
parser.add_argument("backup_path", help="Backup path")
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

def move_files_string_generator(files:List[tuple[str, str]]) -> str:
    mssql_data_path="/var/opt/mssql/data/"
    output = ""
    for file in files:
        output += f"MOVE N'{file[0]}' TO N'{mssql_data_path +file[1].split("\\")[-1]}',"
    return output

def get_files_list(cursor: Cursor, backup_file_path) -> List[tuple[str, str]]: 
    sql_query = f"RESTORE FILELISTONLY FROM DISK = N'{backup_file_path}'"

    cursor.execute(sql_query)

    rows = cursor.fetchall()

    base = []
    for row in rows:
        logical_name = row.LogicalName
        physical_name = row.PhysicalName
        print(f"LogicalName: {logical_name}, PhysicalName: {physical_name}")
        base.append((logical_name, physical_name))
    return base

def get_database_name(cursor: Cursor, backup_file_path) -> str:
    sql_query = f"RESTORE HEADERONLY FROM DISK = N'{backup_file_path}'"

    cursor.execute(sql_query)

    rows = cursor.fetchall()

    for row in rows:
        return row.DatabaseName

def restore_db(cursor: Cursor, database_name: str, backup_file_path: str, files: List[tuple[str, str]]):
    restore_query = f"""
    RESTORE DATABASE [{database_name}]
    FROM DISK = N'{backup_file_path}' WITH
        {move_files_string_generator(files)}
        NOUNLOAD,  STATS = 5;
    """
    
    print(restore_query)
    cursor.execute(restore_query)
    while cursor.nextset():
     pass 
    print(f"Database {database_name} was restored!")
    
try:
    connection = pyodbc.connect(connectionString)
    connection.autocommit = True
    cursor = connection.cursor()
    backup_file_path = args.backup_path
    files = get_files_list(cursor, backup_file_path)
    database_name = get_database_name(cursor, backup_file_path)
    restore_db(cursor, database_name, backup_file_path, files)
    cursor.close()
except Exception as e:
    print(f"Error: {e}")

finally:
    if connection:
        connection.close()


