from flask import Flask, render_template, request, redirect, url_for
from db import get_db


app = Flask(__name__)

@app.route("/")
def forside():
    return render_template("base.html")

@app.route("/om")
def om_oss():
    return render_template("om.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/sok", methods=["GET", "POST"])
def sok():
    return render_template("sok.html")

@app.route("/dbtest")
def dbtest():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT 'Hei fra databasen!'")
        result = cur.fetchone()
        conn.close()
        return f"Database OK: {result[0]}"
    except mysql.connector.Error as e:
        return f"Database error: {e}"

if __name__ == "__main__":
    app.run(debug=True)