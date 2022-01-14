import sqlite3

from sqlalchemy.orm import query

def add_column(database_name, table_name, column_name, data_type):

  connection = sqlite3.connect(database_name)
  cursor = connection.cursor()

  if data_type == "Integer":
    data_type_formatted = "INTEGER"
  elif data_type == "String":
    data_type_formatted = "VARCHAR(100)"

  base_command = ("ALTER TABLE '{table_name}' ADD column '{column_name}' '{data_type}'")
  sql_command = base_command.format(table_name=table_name, column_name=column_name, data_type=data_type_formatted)

  cursor.execute(sql_command)
  connection.commit()
  connection.close()


def query():
    connection = sqlite3.connect("Database.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM ftx_input")
    rows = cursor.fetchall()
    print(rows[-1][-1])


add_column("Database.db","ftx_strategy","symbol","String")

#query()