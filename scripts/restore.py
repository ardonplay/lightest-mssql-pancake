from typing import List
import pyodbc
from pyodbc import Cursor
import os 

# Параметры подключения
server = 'localhost'
database = 'master'  # Обычно запросы восстановления выполняются из базы данных 'master'
username = 'SA'
password = 'R00tIkr@'

# Строка подключения
connectionString = (
    f'DRIVER={{ODBC Driver 18 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password};'
    f'Encrypt=no;'
    f'TrustServerCertificate=yes;'
)

connection = None  # Инициализация переменной connection

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

    print("LogicalName и PhysicalName из резервной копии:")
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
    
    
try:
    connection = pyodbc.connect(connectionString)
    connection.autocommit = True
    cursor = connection.cursor()
    print("Подключение успешно!")
    backup_file_path = "/var/backups/my.bak"
    base = get_files_list(cursor, backup_file_path)
    database_name = get_database_name(cursor, backup_file_path)
    print(database_name)
    restore_query = f"""
    RESTORE DATABASE [{database_name}]
    FROM DISK = N'{backup_file_path}' WITH  FILE = {len(base)},
        {move_files_string_generator(base)}
        NOUNLOAD,  STATS = 5;
    """

    # Выполнение запроса на восстановление базы данных
    cursor.execute(restore_query)
    while cursor.nextset():
     pass 
    cursor.close()
    print("Восстановление базы данных завершено.")
    
except Exception as e:
    print(f"Ошибка: {e}")

finally:
    if connection:
        connection.close()


