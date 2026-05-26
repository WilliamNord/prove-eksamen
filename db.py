# db.py
from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv()

def get_db():
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "eksamen_elev"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "prøve_eksamen")
    )
    return connection