from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

load_dotenv()  # laster inn .env filen

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

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
        
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM users WHERE username=%s", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            # sender en flash-melding til session
            # når brukeren redirectes til signup siden vil base.html vise meldingen
            flash("Dette brukernavnet er allerede tatt")
            conn.close()
            return redirect(url_for("signup"))

        # genererer en hash av passordet med algorytmen "pbkdf2" og metoden "sha256"
        password_hash = generate_password_hash(password, method="pbkdf2:sha256")

        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s,%s)",
            (username, password_hash)
        )

        conn.commit()
        conn.close()

        # sender en flash-melding til session om at brukeren har laget en bruker
        flash("Du har laget en ny bruker")
        return redirect(url_for("login"))

    return render_template("signup.html")

#når du trykker logut sendes du til /logout, session tømmes og du blir sendt til forsiden
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Du har blitt logget ut")
    return redirect(url_for("forside"))

@app.route("/dbtest")
def dbtest():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT 'Hei fra databasen!'")
        result = cur.fetchone()
        # returnerer ('Hei fra databasen!',) og henter første index.
        conn.close()
        return f"Database OK: {result[0]} result tupple: {result} {session['user_id']}"
    except mysql.connector.Error as e:
        return f"Database error: {e}"


if __name__ == "__main__":
    app.run(debug=True)