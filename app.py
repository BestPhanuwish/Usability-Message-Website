'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''
from datetime import timedelta

import eventlet
from flask import Flask, render_template, request, abort, url_for, flash
from flask_socketio import SocketIO
from flask import redirect
import db
import secrets
import bcrypt
import sqlite3
from cryptography.fernet import Fernet
from flask import Flask, request, session, jsonify
from functools import wraps

# import logging

# this turns off Flask Logging, uncomment this to turn off Logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

app = Flask(__name__)

# secret key used to sign the session cookie
app.config['SECRET_KEY'] = secrets.token_hex()
socketio = SocketIO(app)

# don't remove this!!
import socket_routes

message_history_db = {}


# index page
@app.route("/")
def index():
    return render_template("index.jinja")

# welcome page
@app.route("/welcome")
def welcome():
    return render_template("welcome.jinja")

# staff page
@app.route("/staff")
def staff():
    return render_template("staff.jinja")

# login page
@app.route("/login")
def login():
    return render_template("login.jinja")


# friend page
@app.route("/friend")
def friend():
    return render_template("friend.jinja")


# handles a get request to the signup page
@app.route("/signup")
def signup():
    return render_template("signup.jinja")


# handles a post request when the user clicks the signup button
@app.route("/signup/user", methods=["POST"])
def signup_user():
    if not request.is_json:
        abort(404)

    username_enter = request.json.get("username")
    password_enter = request.json.get("password")
    role = int(request.json.get("role"))

    # Generate a salt
    salt = bcrypt.gensalt()
    # Hash the password with the salt
    enc_password = bcrypt.hashpw(password_enter.encode('utf-8'), salt)

    if db.get_user(username_enter) is None:
        db.insert_user(username_enter, enc_password, role)
        print("Now, waiting for following page")
        return url_for('login', username=username_enter)

    return "Error: User already exists!"


# handles a post request when the user clicks the log in button
@app.route("/login/user", methods=["POST"])
def login_user():
    if not request.is_json:
        abort(404)

    Username_ENter = request.json.get("username")
    User_Enter_Pwd = request.json.get("password")
    role = request.json.get("role")

    # Connect to the SQLite database
    conn = sqlite3.connect('database/main.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user WHERE username = ?", (Username_ENter,))
    result = cursor.fetchone()

    if result:
        if result[2] != int(role):
            return "Role not match"
        
        # print("result: ", result)
        hashed_password = result[1]
        
        salt = hashed_password[:29]  # 29 is the length of the salt in bcrypt
        pwd_hashed = hashed_password[29:]

        hashed_user_input_password = bcrypt.hashpw(User_Enter_Pwd.encode('utf-8'), salt)

        if hashed_password != hashed_user_input_password:
            # print("hash_password: ", hashed_password)
            # print("UserEnter_Pwd: ", hashed_user_input_password)
            return "Error Password not match"

        else:
            session['username'] = Username_ENter
            print("Welcome to join chat room")
            return url_for('home', username=request.json.get("username"))
    else:
        return "Error username not found"

# handles a post request when user click home on navigate bar
@app.route("/home/user", methods=["POST"])
def home_user():
    if not request.is_json:
        abort(404)

    return url_for('home', username=request.json.get("username"))

@app.route("/admin/user", methods=["POST"])
def admin_user():
        
    username = session.get("username")
    user = db.get_user(username)
    if user == None or user.role == 0:
        return "Error"

    return url_for('admin', username=username)

# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404


# home page, where the messaging app is
@app.route("/home")
def home():
    if request.args.get("username") is None:
        abort(404)

    certify_username = session.get('username')
    if certify_username is None:
        print("This user not login")
        return redirect(url_for('login'))
    role = db.get_role(certify_username)

    return render_template("home.jinja", username=request.args.get("username"), role=role)

# knowledge repo page, where we can reed article
@app.route("/repo")
def repo():

    certify_username = session.get('username')
    if certify_username is None:
        print("This user not login")
        return redirect(url_for('login'))
    role = db.get_role(certify_username)

    # 调用上面的函数，获取链接
    conn = get_db_connection()
    # 查询所有数据，放到变量posts中
    posts = conn.execute('SELECT * FROM posts order by created desc').fetchall()
    conn.close()

    return render_template("repo.jinja", username=certify_username, role=role, posts=posts)

# craete article page, to publish an article
@app.route("/create")
def create():
    
    certify_username = session.get('username')
    if certify_username is None:
        print("This user not login")
        return redirect(url_for('login'))

    return render_template("new.html", username=certify_username)

# about me page, to see our profile
@app.route("/profile")
def profile():

    certify_username = session.get('username')
    if certify_username is None:
        print("This user not login")
        return redirect(url_for('login'))

    return render_template("profile.jinja", username=certify_username)

# admin page
@app.route("/admin")
def admin():

    username = session.get("username")
    user = db.get_user(username)
    if user == None or user.role == 0:
        print("This user not login or you're not an admin to access this page")
        return redirect(url_for('login'))

    return render_template("admin.jinja", username=username)

# form in admin page submitted
@app.route("/admin/submit", methods=["POST"])
def admin_submit():
    if request.args.get("username") is None:
        abort(404)
    target_usernamme = request.args.get("username")
    
    username = session.get("username")
    user = db.get_user(username)
    if user == None or user.role == 0:
        return "You got logout or you're a student that is not allowed"
    
    if db.get_user(target_usernamme) == None:
        return f"{target_usernamme} not exist"
    
    db.mute_user(target_usernamme)
    
    return f"{target_usernamme} got muted"

@app.route("/admin/submit2", methods=["POST"])
def admin_submit2():
    if request.args.get("username") is None:
        abort(404)
    target_usernamme = request.args.get("username")
    
    username = session.get("username")
    user = db.get_user(username)
    if user == None or user.role == 0:
        return "You got logout or you're a student that is not allowed"
    
    if db.get_user(target_usernamme) == None:
        return f"{target_usernamme} not exist"
    
    db.unmute_user(target_usernamme)
    
    return f"{target_usernamme} got unmuted"

def get_db_connection():
    conn = sqlite3.connect('database/db_info.db')

    conn.row_factory = sqlite3.Row
    return conn

def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()

    comments = conn.execute('SELECT * FROM comments WHERE post_id = ? ORDER BY created DESC', (post_id,)).fetchall()
    conn.close()
    return post, comments


@app.route('/web_index')
def web_index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts order by created desc').fetchall()
    conn.close()

    return render_template('show.html', posts=posts)

def get_author_name():
    certify_username = session.get('username')
    return certify_username

def get_role_for_comment(username):
    conn = sqlite3.connect('database/main.db')
    role = conn.execute('select role from user where username == ?', (username, )).fetchone()
    return role

@app.route('/posts/<int:post_id>/comment', methods=['POST'])
def make_comment(post_id):
    role = request.args.get('role')
    print("role:", role)
    name = request.args.get("username")
    print("name:", name)
    
    certify_username = get_author_name()
    print("certify_username:", certify_username)

    role_certify = get_role_for_comment(certify_username)
    print("role_certify: ", type(role_certify))
    
    comment_text = request.form['comment']
    if not comment_text.strip():
        flash('Comment cannot be empty!', 'error')
        return redirect(url_for('post', post_id=post_id))

    role_number = role_certify[0]

    conn = get_db_connection()
    conn.execute('INSERT INTO comments (body, post_id, author_name, role) VALUES (?, ?, ?, ?)', (comment_text, post_id, certify_username, role_number,) )
    conn.commit()
    conn.close()
    flash('Comment added successfully!', 'success')
    return redirect(url_for('post', post_id=post_id))

@app.route('/posts/<int:post_id>/comments/<int:comment_id>/delete', methods=['POST'])
def delete_comment(post_id, comment_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
    conn.commit()
    conn.close()
    flash('Comment deleted successfully!', 'success')
    return redirect(url_for('post', post_id=post_id))

@app.route('/posts/<int:post_id>')
def post(post_id):
    certify_username = session.get('username')
    if certify_username is None:
        print("This user not login")
        return redirect(url_for('login'))
    role = db.get_role(certify_username)
    
    post, comments = get_post(post_id)
    if not post:
        return "Post not Found"
    
    return render_template('post.html', username=certify_username, role=role, post=post, comments=comments)

def number_for_role(role):
    if role == '0':
        return 'student'
    if role == '1':
        return "staff"
    if role == '2':
        return "administrator"
    if role == '3':
        return "admin"

@app.route('/posts/new', methods=('GET', 'POST'))
def new():
    if request.method == 'POST':
        
        username = session.get('username')
        if username is None:
            print("This user not login")
            return redirect(url_for('login'))
        
        title = request.form['title']
        content = request.form['content']
        role = db.get_role(username)

        if not title:
            flash("The title cannot be empty", category='error')
            return redirect(url_for('repo'))
        elif not content:
            flash("Content cannot be empty", 'info')
            return redirect(url_for('repo'))
        elif db.is_mute(username) == True:
            flash("You got muted, unable to post article", category='error')
            return redirect(url_for('repo'))
        else:
            conn = get_db_connection()
            conn.execute('insert into posts (title, content, author, role) values(?, ?, ?, ?)', (title, content, username, role, ))            
            conn.commit()
            conn.close()
            flash("saved successfully", 'success')
            return redirect(url_for('repo'))

    return render_template('new.html')

@app.route('/posts/<int:post_id>/edit', methods=('GET', 'POST'))
def edit(post_id):
    post = get_post(post_id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('title can not be empty')
        else:
            conn = get_db_connection()
            conn.execute('Update posts SET title = ?, content = ?'
                         'Where id = ?',
                         (title, content, post_id))
            conn.commit()
            conn.close()
            return redirect(url_for('repo'))

    return render_template('edit.html', post=post)

@app.route('/posts/<int:post_id>/delete', methods=('POST',))
def delete(post_id):
    post = get_post(post_id)
    conn = get_db_connection()
    conn.execute('DELEte from posts where id =?', (post_id, ))
    conn.commit()
    conn.close()
    flash('delete successful!')
    return redirect(url_for('repo'))

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/search', methods=['POST'])
def search():
    keyword = request.form['keyword']
    
    articles = search_articles(keyword)

    return render_template('search_results.html', articles=articles)

def search_articles(keyword):
    conn = sqlite3.connect('database/db_info.db')
    cursor = conn.cursor()

    search_pattern = f'%{keyword}%'
    query = "SELECT id, title FROM posts WHERE title LIKE ? OR content LIKE ?"

    cursor.execute(query, (search_pattern, search_pattern))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results



if __name__ == '__main__':
    socketio.run(app)
    """
    # If you had https you can uncomment this part
    ssl_args = {
        'certfile': './database/new_localhost.crt',
        'keyfile': './database/new_localhost.key'
    }

    listener = eventlet.listen(('localhost', 5000))

    ssl_listener = eventlet.wrap_ssl(listener, **ssl_args, servere_side=True)

    eventlet.wsgi.server(ssl_listener, app)
    """
