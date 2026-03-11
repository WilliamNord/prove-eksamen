from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv()

def get_db():
    connection = mysql.connector.connect(
        host="localhost",
        user="eksamen_elev",
        # henter hemmelig passord fra .env filen
        password=os.getenv("DB_PASSWORD"),
        database="prøve_eksamen"
    )
    return connection