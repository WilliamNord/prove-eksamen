from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

#henter .env filen
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# henter krypteringsnøkkelen fra .env
fernet = Fernet(os.getenv("MESSAGE_KEY"))

@app.route("/")
def forside():
    return render_template("index.html")

@app.route("/om")
def om_oss():
    return render_template("om.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/settings", methods=["GET", "POST"])
def settings():

    if not session.get("user_id"):
        flash("Du må være logget inn for å se innstillinger")
        return redirect(url_for("login"))

    if request.method == "POST":
        user_id = session.get("user_id")
        confirm = request.form["username"]

        if confirm != session.get("username"):
            flash("Bekreftelse mislyktes. Skriv inn ditt brukernavn for å bekrefte.")
            return redirect(url_for("settings"))

        conn = get_db()
        cur = conn.cursor()

        # sletter meldinger først, så foreign key ikke krasjer
        cur.execute("DELETE FROM messages WHERE sender_id = %s OR receiver_id = %s", (user_id, user_id))

        # sletter så brukeren
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        conn.close()

        session.clear()
        flash("Brukeren din har blitt slettet.")
        
        return redirect(url_for("forside"))

    return render_template("settings.html")


@app.route("/messages")
@app.route("/messages/<int:other_user_id>")
def messages(other_user_id=None):
    if not session.get("user_id"):
        flash("Du må være logget inn for å se meldingene dine")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    conn = get_db()
    #henter data som keys og values
    cur = conn.cursor(dictionary=True)

    # Henter alle brukere du har hatt samtale med
    cur.execute("""
        SELECT DISTINCT u.id, u.username
        FROM users u
        JOIN messages m ON (m.sender_id = u.id OR m.receiver_id = u.id)
        WHERE (m.sender_id = %s OR m.receiver_id = %s)
        AND u.id != %s
    """, (user_id, user_id, user_id))
    conversations = cur.fetchall()

    # Henter alle brukere som ikke er deg
    cur.execute("SELECT id, username FROM users WHERE id != %s", (user_id,))
    all_users = cur.fetchall()

    # Henter meldinger i den åpne samtalen (hvis det er en)
    msgs = []
    if other_user_id:
        cur.execute("""
            SELECT m.content AS message, u.username
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE (m.sender_id = %s AND m.receiver_id = %s)
               OR (m.sender_id = %s AND m.receiver_id = %s)
            ORDER BY m.sent_at ASC
        """, (user_id, other_user_id, other_user_id, user_id))
        row_msgs = cur.fetchall()

        for msg in row_msgs:
            msg["message"] = fernet.decrypt(msg["message"].encode()).decode()
        msgs = row_msgs

    conn.close()

    # laster meldinger med informasjonen mentet over
    return render_template("messages.html",
        conversations=conversations,
        messages=msgs,
        other_user_id=other_user_id,
        all_users=all_users
    )


@app.route("/send_message", methods=["POST"])
def send_message():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    sender_id = session["user_id"]
    receiver_id = request.form["receiver_id"]
    message = request.form["message"]
    
    # krypterer meldingen før den lagres i databasen
    encrypted_message = fernet.encrypt(message.encode()).decode()

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (sender_id, receiver_id, content) VALUES (%s, %s, %s)",
        (sender_id, receiver_id, encrypted_message)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("messages", other_user_id=receiver_id))

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
            session["username"] = username
            return redirect(url_for("forside"))
        else:
            flash("Feil brukernavn eller passord")
            return redirect(url_for("login"))

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
    session.clear()
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
    except Exception as e:
        return f"Database error: {e}"


if __name__ == "__main__":
    app.run(debug=True)