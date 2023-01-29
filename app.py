from flask import Flask, redirect, render_template , request, session, jsonify, make_response, flash
import os, datetime, pytz
from cs50 import SQL
from flask_session import Session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["secret_key"] = os.urandom(100000000)
app.config['WTF_CSRF_SECRET_KEY'] = app.config["secret_key"]


db = SQL("sqlite:///media.db")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config["location"] = []
app.config["session_location"] = 0
app.config['UPLOAD_FOLDER'] = 'static/posts'

def convert_time_format(time_str):
    new = str(time_str)
    h, m, s = new.split(":")
    m = int(m) % 60
    h = int(h) % 24
    time = "{} hours and {} minutes ago".format(h, m)
    return time


def time_since(posts):
    if 'created_at' in posts:
        time = posts['created_at']
        time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
        since = datetime.datetime.now() - time
        return convert_time_format(since)
    return None


@app.route("/", methods=["GET", "POST"])
def index():

    app.config["session_location"] += 1

    if session.get("userid") is None:
         return redirect("/login")
    
    elif app.config["session_location"] % 3 != 0:
        return redirect("/loading")

    elif not app.config["location"]:
        return redirect("/loading")

    else:
        
        app.config["session_location"] = 0

        print(app.config["location"])
        latitude = app.config["location"][1]
        longitude = app.config["location"][0]

        posts = db.execute(f"SELECT * FROM posts WHERE (6371 * acos(cos(radians({latitude})) * cos(radians(latitude)) * cos(radians(longitude) - radians({longitude})) + sin(radians({latitude})) * sin(radians(latitude)))) <= (1/6371) ")
        posts_list = []


        for post in posts:
            posts_list.append({
            'post': post,
            'time_since': time_since(post),
            'username': db.execute("SELECT users.username, user_id FROM posts JOIN users ON posts.user_id = users.id WHERE user_id=? LIMIT 1", post['user_id'])
        })

        for data in posts_list:
            print(data['time_since'])

        return render_template("index.html", posts_list=posts_list)
        

def allowed_file(filename):
    return filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/posting", methods=["GET", "POST"])
def posting():

    if request.method == "GET":
        return redirect('/')

    else:

        if not app.config["location"]:
            return redirect('/loading')

        if 'file' not in request.files:
            return redirect("/posting")

        file = request.files['file']

        if file.filename == '':
            return redirect('/posting')

        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], filename))
            # file.save('/folder')

            
            if not app.config["location"]:
                return redirect("/login")
            else:
                latitude = app.config["location"][1]
                longitude = app.config["location"][0]
                caption = request.form.get("caption")
                time_created= datetime.datetime.now(pytz.timezone('US/Eastern'))
                db.execute("INSERT INTO posts (user_id, created_at, content, likes, caption, latitude, longitude) VALUES(?, ?, ?, ?, ?, ?, ?)", session["userid"], time_created, filename, 0 , caption , latitude, longitude)


        return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":

        return render_template("login.html")
        
    else:

        session.clear()

        username = request.form.get("username")

        userid = db.execute("SELECT id FROM users WHERE username = ?", username)

        if not userid:
            flash('Wrong Username', category='error')
            return render_template("login.html")

        hash = db.execute("SELECT password FROM users where id = ?", userid[0]["id"])

        if not check_password_hash(hash[0]["password"], request.form.get("password")):
            flash('Wrong Password', category='error')
            return render_template("login.html" )
         
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

        print(generate_password_hash(password))

        if not exist:
            if password != password_confirm:
                return redirect("/register")
            else:
                time_created= datetime.datetime.now(pytz.timezone('US/Eastern'))
                db.execute("INSERT INTO users (username, password, created_at) VALUES(?, ?, ?)", username, generate_password_hash(password), time_created)
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

    app.config["location"] = []

    app.config["location"].append(req["longitude"])
    app.config["location"].append(req["latitude"])

    res = make_response(jsonify({"message": "Message Received"}), 200)

    return "doesn't matter"




             