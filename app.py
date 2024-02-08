import logging
import string
import traceback
import random
import sqlite3
from datetime import datetime
from flask import * # Flask, g, redirect, render_template, request, url_for
from functools import wraps

app = Flask(__name__)

# These should make it so your Flask app always returns the latest version of
# your HTML, CSS, and JS files. We would remove them from a production deploy,
# but don't change them here.
app.debug = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache"
    return response



def get_db():
    db = getattr(g, '_database', None)

    if db is None:
        db = g._database = sqlite3.connect('db/watchparty.sqlite3')
        db.row_factory = sqlite3.Row
        setattr(g, '_database', db)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    db = get_db()
    cursor = db.execute(query, args)
    print("query_db")
    print(cursor)
    rows = cursor.fetchall()
    db.commit()
    cursor.close()
    if rows:
        if one: 
            return rows[0]
        return rows
    return None

def new_user():
    name = "Unnamed User #" + ''.join(random.choices(string.digits, k=6))
    password = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    api_key = ''.join(random.choices(string.ascii_lowercase + string.digits, k=40))
    u = query_db('insert into users (name, password, api_key) ' + 
        'values (?, ?, ?) returning id, name, password, api_key',
        (name, password, api_key),
        one=True)
    print("new user: u ", u)
    return u

def get_user_from_cookie(request):
    user_id = request.cookies.get('user_id')
    password = request.cookies.get('user_password')
    if user_id and password:
        return query_db('select * from users where id = ? and password = ?', [user_id, password], one=True)
    return None

def render_with_error_handling(template, **kwargs):
    try:
        return render_template(template, **kwargs)
    except:
        t = traceback.format_exc()
        return render_template('error.html', args={"trace": t}), 500

# ------------------------------ NORMAL PAGE ROUTES ----------------------------------

@app.route('/')
def index():
    print("index") # For debugging
    user = get_user_from_cookie(request)

    if user:
        rooms = query_db('select * from rooms')
        return render_with_error_handling('index.html', user=user, rooms=rooms)
    
    return render_with_error_handling('index.html', user=None, rooms=None)

@app.route('/rooms/new', methods=['GET', 'POST'])
def create_room():
    print("create room") # For debugging
    user = get_user_from_cookie(request)
    if user is None: return {}, 403

    if (request.method == 'POST'):
        name = "Unnamed Room " + ''.join(random.choices(string.digits, k=6))
        room = query_db('insert into rooms (name) values (?) returning id', [name], one=True)            
        return redirect(f'{room["id"]}')
    else:
        return app.send_static_file('create_room.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    print("signup")
    user = get_user_from_cookie(request)

    if user:
        return redirect('/profile')
        # return render_with_error_handling('profile.html', user=user) # redirect('/')
    
    if request.method == 'POST':
        u = new_user()
        print("u")
        print(u)
        for key in u.keys():
            print(f'{key}: {u[key]}')

        resp = redirect('/profile')
        resp.set_cookie('user_id', str(u['id']))
        resp.set_cookie('user_password', u['password'])
        return resp
    
    return redirect('/login')

@app.route('/profile')
def profile():
    print("profile")
    
    user = get_user_from_cookie(request)
    print("------/profile------",request)
    if user:
        return render_with_error_handling('profile.html', user=user)
    
    redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    print("login")
    user = get_user_from_cookie(request)

    print("login request: ", request)
    
    if user:
        return redirect('/')
    print("login request.method: ", request.method)
    print("login request.json", request.form)
    if request.method == 'POST':
        name = request.form['username']
        password = request.form['password']
        u = query_db('select * from users where name = ? and password = ?', [name, password], one=True)
        # print("login information here : user_id",str(u['id']))
        # print("login information here : user_password",u['password'])
        if u:
            resp = make_response(redirect("/"))

            resp.set_cookie('user_id', str(u['id']))
            resp.set_cookie('user_password', u['password'])
            return resp
        else:
            return render_with_error_handling('login.html', failed=True)   
    return render_with_error_handling('login.html')   

@app.route('/logout')
def logout():
    resp = make_response(redirect('/'))
    resp.set_cookie('user_id', '')
    resp.set_cookie('user_password', '')
    return resp

@app.route('/rooms/<int:room_id>')
def room(room_id):
    user = get_user_from_cookie(request)
    if user is None: return redirect('/')

    room = query_db('select * from rooms where id = ?', [room_id], one=True)
    return render_with_error_handling('room.html',
            room=room, user=user)

# -------------------------------- API ROUTES ----------------------------------

# POST to change the user's name
@app.route('/api/user/name', methods=['POST'])
def update_username():
    user = get_user_from_cookie(request)
    if not user:
        return {}, 403
    print("data in update_username of app.py", request.json)
    new_name = request.json.get('name')
    api_key = request.headers.get('Authorization')
    query_db('update users set name = ? where api_key = ?', [new_name, api_key])
    return {}, 200


# POST to change the user's password
@app.route('/api/user/password', methods=['POST'])
def update_password():
    print("update_password +++++++++++++" ,update_password)
    user = get_user_from_cookie(request)
    if not user:
        return {}, 403

    new_password = request.json.get('password')
    api_key = request.headers.get('Authorization')
    query_db('update users set password = ? where api_key = ?', [new_password, api_key])
    return {}, 200



# POST to change the name of a room
@app.route('/api/rooms/<int:room_id>', methods=['POST'])
def update_room_name(room_id):
    user = get_user_from_cookie(request)
    if not user:
        return {}, 403
    print("user -------------- ", request.json)
    new_name = request.json.get('name')
    print("new_name",new_name)
    # room_id = request.json.get('id')
    print("room_id", room_id)
    query_db('update rooms set name = ? where id = ?', [new_name, room_id])
    print("update the room name here ----------------")
    return {}, 200


# GET to get all the messages in a room
@app.route('/api/rooms/<int:room_id>/messages', methods=['GET'])
def get_messages(room_id):
    user = get_user_from_cookie(request)
    if not user:
        return {}, 403
    
    message = query_db('select * from messages left join users on messages.user_id = users.id where room_id = ?', [room_id])
    if message:
        print("GET MESSAGE SUCCESSFULLY!!!")
        return jsonify([dict(message) for message in message]), 200
    else:
        return jsonify([]), 200



# POST to post a new message to a room
@app.route('/api/rooms/<int:room_id>/messages', methods=['POST'])
def post_message(room_id):
    user = get_user_from_cookie(request)
    print("user in post_message of app.py: ", user)
    if not user:
        return {}, 403
    
    api_key = request.headers.get('Authorization')
    user_id = query_db('select id from users where api_key = ?', [api_key],one = True)['id']
    print("user_id in post_message of app.py: ", user_id)
    body = request.json.get('body')
    query_db('insert into messages (user_id, room_id, body) values (?, ?, ?)', [user_id, room_id, body])
    return {}, 200

