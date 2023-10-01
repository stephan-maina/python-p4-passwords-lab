from flask import Flask, request, jsonify, session, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from config import Config
from models import db, User
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
bcrypt = Bcrypt(app)

@app.route('/')
def home():
    if 'user_id' in session:
        return f'Hello, {session["username"]}! <a href="/logout">Logout</a>'
    return 'Welcome! <a href="/login">Login</a> or <a href="/signup">Signup</a>'

@app.route('/signup', methods=['POST'])
def signup():
    if 'user_id' in session:
        return jsonify({'message': 'You are already signed in'}), 400

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        return jsonify({'message': 'Username already exists'}), 400

    new_user = User(username=username)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    session['user_id'] = new_user.id
    session['username'] = new_user.username

    return jsonify({'message': 'Signup successful', 'user': {'id': new_user.id, 'username': new_user.username}})

@app.route('/login', methods=['POST'])
def login():
    if 'user_id' in session:
        return jsonify({'message': 'You are already signed in'}), 400

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid username or password'}), 401

    session['user_id'] = user.id
    session['username'] = user.username

    return jsonify({'message': 'Login successful', 'user': {'id': user.id, 'username': user.username}})

@app.route('/logout', methods=['DELETE'])
def logout():
    if 'user_id' not in session:
        return jsonify({'message': 'You are not signed in'}), 401

    session.clear()
    return jsonify({'message': 'Logout successful'})

if __name__ == '__main__':
    app.run(debug=True)

