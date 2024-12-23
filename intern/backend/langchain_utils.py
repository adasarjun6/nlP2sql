# table_details.py

import os
from dotenv import load_dotenv
import pymysql
from langchain_community.utilities.sql_database import SQLDatabase

load_dotenv()

db_user = os.getenv("db_user")
db_password = os.getenv("db_password")
db_host = os.getenv("db_host")
db_name = os.getenv("db_name")

def select_table(question):
    # Logic to determine relevant tables based on the question
    return ["clients", "projects"]  # Example: Replace with your actual logic

def answer_question(question, sql_result):
    # Logic to generate the answer based on the question and SQL result
    return f"Answer to '{question}' based on SQL result: {sql_result}"  # Example: Replace with your actual logic

def execute_sql_query(sql_query):
    # Execute SQL query and fetch result
    db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")
    with db.get_connection() as conn:
        result = conn.execute(sql_query).fetchall()
        sql_result = str(result)
    return sql_result
