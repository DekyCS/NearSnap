from flask import Flask, url_for
from cs50 import SQL
from flask import redirect, render_template , request, session
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


@app.route("/", methods=["GET", "POST"])
def index():

    if session.get("userid") is None:
         return redirect("/login")
    
    elif session.get("location") is None:
        return redirect("/loading")

    else:
        

        latitude = session["latitude"]
        longitude = session["longitude"]
        posts = db.execute(f"SELECT * FROM posts WHERE (6371 * acos(cos(radians({latitude})) * cos(radians(latitude)) * cos(radians(longitude) - radians({longitude})) + sin(radians({latitude})) * sin(radians(latitude)))) < 1  ")
        return render_template("index.html", posts)
        

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

@app.route("/upload")
def upload():
    return render_template("upload.html")

# @app.route("/addpic" , methods=["POST"])


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect("/")


@app.route("/location", methods=["POST"])
def location():

    latitude = request.json['latitude']
    longitude = request.json['longitude']


    session['latitude'] = latitude
    session['longitude'] = longitude

    return redirect("/")
    

@app.route("/loading")
def loading():

    
    return render_template("loading.html")


@app.route("/reload")
def reload():
    session["latitude"].clear()
    session["longitude"].clear()
    return redirect("/loading")




            

