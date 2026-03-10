from flask import Flask, render_template, request, redirect, url_for, session
from db import get_db
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "hemmelig_nokkel"

@app.route("/")
def forside():
    return render_template("index.html")

@app.route("/om")
def om_oss():
    return render_template("om.html")

@app.route("/messages")
def messages():
    return render_template("messages.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()

        # henter er tuple med brukerens id og hashed passord
        cur.execute(
            "SELECT id, password_hash FROM users WHERE username=%s",
            (username,)
        )

        user = cur.fetchone()

        conn.close()

        #check_password_hash sammenligner to hashede verdier.
        if user and check_password_hash(user[1], password):
            #lagrer i session at du er logget in og sender deg tilbake til forsiden.
            session["user_id"] = user[0]
            return redirect(url_for("forside"))
        else:
            return "Feil brukernavn eller passord"

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":
        #henter det som er skrevet i skjemaet i /signup siden
        username = request.form["username"]
        password = request.form["password"]

        # genererer en hash av passordet med algorytmen "pbkdf2" og metoden "sha256"
        password_hash = generate_password_hash(password, method="pbkdf2:sha256")

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s,%s)",
            (username, password_hash)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/dbtest")
def dbtest():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT 'Hei fra databasen!'")
        result = cur.fetchone()
        # returnerer ('Hei fra databasen!',) og henter første index.
        conn.close()
        return f"Database OK: {result[0]} result tupple: {result}"
    except mysql.connector.Error as e:
        return f"Database error: {e}"

if __name__ == "__main__":
    app.run(debug=True)