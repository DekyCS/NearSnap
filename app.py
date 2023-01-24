from flask import Flask, url_for
from cs50 import SQL
from flask import redirect, render_template , request, session, jsonify, make_response
from flask_session import Session
from flask_sockets import Sockets


# from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
sockets = Sockets(app)

app.secret_key = "uytgfviygf9876gyfv786gyf876t7678ft"

db = SQL("sqlite:///media.db")

location = []
app.config["session_location"] = 0

@app.route("/", methods=["GET", "POST"])
def index():

    app.config["session_location"] += 1

    if session.get("userid") is None:
         return redirect("/login")
    
    elif app.config["session_location"] % 3 != 0:
        return redirect("/loading")

    else:
        
        app.config["session_location"] = 0

        print(location)

        #posts = db.execute(f"SELECT * FROM posts WHERE (6371 * acos(cos(radians({latitude})) * cos(radians(latitude)) * cos(radians(longitude) - radians({longitude})) + sin(radians({latitude})) * sin(radians(latitude)))) < 1  ")
        return render_template("index.html")
        

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":

        return render_template("login.html")
        
    else:

        session.clear()

        username = request.form.get("username")
        password = request.form.get("password")


        userid = db.execute("SELECT id FROM users WHERE username = ? AND password = ? ", username, password)

        if not userid:
            return render_template("login.html")
         
        session["userid"] = userid[0]["id"]
          
        return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    
    if request.method == "GET":
        return render_template("register.html")

    else:

        username = request.form.get("username")
        password = request.form.get("password")
        password_confirm = request.form.get("password2")

        exist = db.execute("SELECT * FROM users WHERE username = ?", username)

        if not exist:
            if password != password_confirm:
                return redirect("/register")
            else:
                db.execute("INSERT INTO users (username, password) VALUES(?, ?)", username, password)
                return redirect("/")

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect("/")

@app.route("/loading")
def loading():
    return render_template("loading.html")

@app.route("/loading/create-entry", methods=["POST"])
def create_entry():

    req = request.get_json()

    app.config["session_location"] += 1

    location.append(req["longitude"])
    location.append(req["latitude"])

    res = make_response(jsonify({"message": "Message Received"}), 200)

    return "doesn't matter"

            

