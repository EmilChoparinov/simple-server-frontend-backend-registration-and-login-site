from flask import Flask, render_template, request, flash, redirect
from mysqlconnection import MySQLConnector
import re
import os, binascii, md5

NAME_REGEX = re.compile(r'^[A-Za-z]+$')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

server = Flask(__name__)
mysql = MySQLConnector(server, 'login_and_registration')

server.secret_key = 'a secret key'

@server.route('/')
def index():
    return redirect('/register')

@server.route('/register')
def register():
    return render_template('register.html')

@server.route('/login')
def login():
    return render_template('login.html')

@server.route('/process_reg', methods=['POST'])
def process_reg():
    isFailed = False
    if not NAME_REGEX.match(request.form['first_name']) or not NAME_REGEX.match(request.form['last_name']):
        flash('Name not valid! Can only contain letters!')
        isFailed = True
    if len(request.form['first_name']) < 3 or len(request.form['last_name']) < 3  :
        flash('Name not valid! Must have at least to characters!')
        isFailed = True
    if not EMAIL_REGEX.match(request.form['email']):
        flash('Email not valid!')
        isFailed = True
    if len(request.form['password']) < 8:
        flash('Password must be at least 8 characters long!')
        isFailed = True
    if request.form['password'] != request.form['confirm_password']:
        flash('Passwords do not match!')
        isFailed = True
    
    if not isFailed:
        query = "SELECT * FROM users WHERE users.email = :email LIMIT 1"
        callback = mysql.query_db(query, data={'email': request.form['email']})
        print len(callback)
        if len(callback) == 0:
            query = "INSERT INTO users (users.first_name, users.last_name, users.email, users.password, users.salt, users.created_at, users.edited_at) VALUE (:first_name, :last_name, :email, :password, :salt,  NOW(), NOW())"
            salt = binascii.b2a_hex(os.urandom(15))
            hsh_pw = md5.new(request.form['password'] + salt).hexdigest()
            data = {
                'first_name': request.form['first_name'],
                'last_name': request.form['last_name'],
                'email': request.form['email'],
                'password': hsh_pw,
                'salt': salt
            }
            mysql.query_db(query, data)
        else:
            flash('account already exists!')
            isFailed = True
    if not isFailed:
        return redirect('/success')
    return redirect('/register')

@server.route('/process_log', methods=['POST'])
def process_log():
    query = "SELECT * FROM users WHERE users.email = :email LIMIT 1"
    callback = mysql.query_db(query, data={'email': request.form['email']})
    print callback
    if len(callback) != 0:
        test_pw = md5.new(request.form['password'] + callback[0]['salt']).hexdigest()
        if callback[0]['password'] == test_pw:
            return redirect('/success')
        else:
            flash('Passwords do not match!')
            return redirect('/login')
    else:
        flash('Email does not exist!')
    return redirect('/login')

@server.route('/success')
def success():
    return render_template('success.html')

server.run(debug=True)