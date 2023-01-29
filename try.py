import datetime
from cs50 import SQL


db = SQL("sqlite:///media.db")
posts = db.execute("SELECT * FROM posts")

def time_since(posts):
    time_passed_list = []
    if "created_at" in posts:
        timestamp = posts['created_at']
        timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
        time_passed = datetime.datetime.now() - timestamp
        time_passed_list.append(time_passed)
    return time_passed_list


print(time_since(posts))



