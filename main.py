from flask import Flask, redirect, render_template , request, session, jsonify, make_response, flash, g
import os, datetime, pytz
from flask_session import Session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = '35.229.66.34'
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = 'nearfaceo&a2023'
app.config['MYSQL_DB'] = 'nearsnap'

mysql = MySQL(app)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["secret_key"] = os.urandom(100000000)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config["location"] = []
app.config["session_location"] = 0
app.config['UPLOAD_FOLDER'] = 'static/posts'

def convert_time_format(time_str):
    new = str(time_str)
    if "," in new:
        date, new = new.split(",")
    else:
        date = None
    h, m, s = new.split(":")
    m = int(m) % 60
    h = h.split(',')[-1].strip()
    h = int(h) % 24
    if date:
        time = "{} ago".format(date)
    else:
        time = "{} hours and {} minutes ago".format(h, m)
    return time


def time_since(posts):
    if posts[3] != "":
        time = posts[3]
        time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')
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
        

        cursor = mysql.connection.cursor()

        app.config["session_location"] = 0

        # print(app.config["location"])
        latitude = app.config["location"][1]
        longitude = app.config["location"][0]

        cursor.execute(f"SELECT * FROM posts WHERE (6371 * acos(cos(radians({latitude})) * cos(radians(latitude)) * cos(radians(longitude) - radians({longitude})) + sin(radians({latitude})) * sin(radians(latitude)))) <= 10")
        posts = cursor.fetchall()
        posts_list = []
        
        for post in posts:
            cursor.execute("SELECT users.username, user_id FROM posts JOIN users ON posts.user_id = users.id WHERE user_id=%s LIMIT 1", (post[1],))
            user = cursor.fetchall()
            posts_list.append({
            'post': post,
            'time_since': time_since(post),
            'username': user                 
        })

        print(posts_list[0]["post"][6])

        cursor.close()

        return render_template("index.html", posts_list=posts_list[::-1])
        

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

                cursor = mysql.connection.cursor()


                latitude = app.config["location"][1]
                longitude = app.config["location"][0]
                caption = request.form.get("caption")
                time_created= datetime.datetime.now()
                cursor.execute("INSERT INTO posts (user_id, created_at, content, caption, latitude, longitude) VALUES(%s, %s, %s, %s, %s, %s)", (session["userid"], time_created, filename, caption, latitude, longitude))
                mysql.connection.commit()
                cursor.close()


        return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":

        return render_template("login.html")
        
    else:

        session.clear()

        username = request.form.get("username")

        cursor = mysql.connection.cursor()

        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        userid = cursor.fetchall()

        if not userid:
            flash('Wrong Username', category='error')
            return render_template("login.html")

        cursor.execute("SELECT password FROM users where id = %s", (userid[0][0],))

        hash = cursor.fetchall()

        if not check_password_hash(hash[0][0], request.form.get("password")):
            flash('Wrong Password', category='error')
            return render_template("login.html" )
         
        session["userid"] = userid[0][0]

        cursor.close()
          
        return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    
    if request.method == "GET":
        return render_template("register.html")

    else:

        username = request.form.get("username")
        password = request.form.get("password")
        password_confirm = request.form.get("password2")

        cursor = mysql.connection.cursor()

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        exist = cursor.fetchall()

        print(exist)

        if not exist:
            if password != password_confirm:
                return redirect("/register")
            else:
                time_created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(time_created)
                cursor.execute("INSERT INTO users (username, password, created_at) VALUES(%s, %s, %s)", (username, generate_password_hash(password), time_created,))
                mysql.connection.commit()
                cursor.close()
                return redirect("/")
        else:
            return redirect("/register")

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

if __name__ == '__main__':
    app.run(debug=True)


             
