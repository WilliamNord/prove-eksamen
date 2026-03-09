import mysql.connector

def get_db():
    connection = mysql.connector.connect(
        host="localhost",
        user="eksamen_elev",
        password="DatabasePassord",
        database="prøve_eksamen"
    )
    return connection