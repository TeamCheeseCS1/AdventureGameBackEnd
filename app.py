import hashlib
import json
from time import time
from uuid import uuid4
import random
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from flask_bcrypt import Bcrypt

from flask import Flask, jsonify, request, render_template, make_response
from pusher import Pusher
from decouple import config

from room import Room
from world import World

from models import *
from flask_sqlalchemy import SQLAlchemy

from world import test
import bcrypt

# Look up decouple for config variables
pusher = Pusher(app_id=config('PUSHER_APP_ID'), key=config(
    'PUSHER_KEY'), secret=config('PUSHER_SECRET'), cluster=config('PUSHER_CLUSTER'))

world = World()
JWT_SECRET = config('SECRET')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///gametest.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bcrypt = Bcrypt(app)

class Player(db.Model):
    __tablename__ = 'player'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    location_room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=True)

    def __init__(self, username, password, location_id=None):
        self.username = username
        self.password = password
        self.location_room_id = location_id

    def __repr__(self):
        return '<id {}>'.format(self.id)


class Room(db.Model):
    __tablename__ = 'room'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(), nullable=False)
    description = db.Column(db.String(), nullable=True)
    exit_north_room_id = db.Column(db.Integer, nullable=True)
    exit_south_room_id = db.Column(db.Integer, nullable=True)
    exit_west_room_id = db.Column(db.Integer, nullable=True)
    exit_east_room_id = db.Column(db.Integer, nullable=True)

    def __init__(self, title, description, exit_north_room_id, exit_south_room_id, exit_west_room_id,
                 exit_east_room_id):
        self.title = title
        self.description = description
        self.exit_north_room_id = exit_north_room_id
        self.exit_south_room_id = exit_south_room_id
        self.exit_west_room_id = exit_west_room_id
        self.exit_east_room_id = exit_east_room_id

    def __repr__(self):
        return '<id {}>'.format(self.id)


class Item(db.Model):
    __tablename__ = 'item'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(), nullable=False)
    location_room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=True)


    def __init__(self, name, location_room_id, player_id, shop_id):
        self.name = name
        self.location_room_id = location_room_id
        self.player_id = player_id
        self.shop_id = shop_id


    def __repr__(self):
        return '<id {}>'.format(self.id)


class Shop(db.Model):
    __tablename__ = 'shop'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<id {}>'.format(self.id)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


# def get_player_by_header(world, auth_header):
#     if auth_header is None:
#         return None

#     auth_key = auth_header.split(" ")
#     if auth_key[0] != "Token" or len(auth_key) != 2:
#         return None

#     player = world.get_player_by_auth(auth_key[1])
#     return player


@app.route('/api/registration/', methods=['POST'])
def register():
    values = request.get_json()
    required = ['username', 'password1', 'password2']

    if not all(k in values for k in required):
        response = {'message': "Missing Values"}
        return jsonify(response), 400

    username = values.get('username')
    password1 = values.get('password1')
    password2 = values.get('password2')

    if password1 != password2:
        return {'error': "Passwords do not match"}
    elif len(username) <= 2:
        return {'error': "Username must be longer than 2 characters"}
    elif len(password1) <= 5:
        return {'error': "Password must be longer than 5 characters"}

    password_hash = bcrypt.hashpw(password1.encode(), bcrypt.gensalt())

    new_user = Player(username=username, password=password_hash, location_id=None)
    db.session.add(new_user)
    db.session.commit()


    return {},200
# users = Player.query.order_by(Player.id).all()
# for p in users: 
#     if p.location_room_id == Room.id:
#         players = []
#         players.append(p)
#         print(players)

@app.route('/')
def root():
    return "nothin"

def get_room_players(users, player):
    players = []
    for u in users:
        if u.location_room_id == player.location_room_id:
            players.append(u.username)
    return players

@app.route('/api/login/', methods=['POST'])
def login():
    req = request.json
    user = Player.query.filter_by(username=req["username"]).first()
    players = Player.query.all()
    if user and Bcrypt.check_password_hash(user.password, req["password"]):
        token = jwt.encode({'id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, 'JWT_SECRET')


        user.location_room_id = random.randint(1, 100)
        db.session.commit()
        fun_results = get_room_players(players, user)
        print(fun_results)
        response = {
            'username': user.username,
            'key': token.decode("ascii"),
            'id': user.id,
            'location_room_id': user.location_room_id,
            'players': fun_results
        }
        return jsonify(response), 200
    else:
        return make_response("Invalid Credentials provided", 401)



# @app.route('/api/adv/init/', methods=['GET'])
# def init():
#     player = get_player_by_header(world, request.headers.get("Authorization"))
#     if player is None:
#         response = {'error': "Malformed auth header"}
#         return jsonify(response), 500

#     response = {
#         'title': player.current_room.name,
#         'description': player.current_room.description,
#     }
#     return jsonify(response), 200


@app.route('/api/adv/move/', methods=['POST'])
def move():
    # player = get_player_by_header(world, request.headers.get("Authorization"))
    # if player is None:
    #     response = {'error': "Malformed auth header"}
    #     return jsonify(response), 500
    values = request.get_json()
    required = ['direction', 'username']
    if not all(k in values for k in required):
        response = {'message': "Missing Values"}
        return jsonify(response), 400
    user = Player.query.filter_by(username=values["username"]).first()
    print(user.location_room_id)
    next_id = user.location_room_id
    room = Room.query.filter_by(id=next_id).first()
    direction = values.get('direction')
    print(room)
    players = Player.query.all()

    players_list = get_room_players(players, user)
    if direction == "n":
        if room.exit_north_room_id:
            print(Room)
            
            n_room = Room.query.filter_by(id=room.exit_north_room_id).first()
            user.location_room_id = room.exit_north_room_id
            db.session.commit()
            response = {
            'title': n_room.title,
            'description': n_room.description,
            'players': players_list,
            'current_location_id': user.location_room_id
            # 'items': items...
            }
            return jsonify(response), 200
        else:
            response = {
            'error_msg': "You cannot move in that direction.",
            }
            return jsonify(response), 500
    elif direction == "s":
        if room.exit_south_room_id:
            s_room = Room.query.filter_by(id=room.exit_south_room_id).first()
            user.location_room_id = room.exit_south_room_id
            db.session.commit()
            response = {
            'title': s_room.title,
            'description': s_room.description,
            'players': players_list,
            # 'items': items...
            }
            return jsonify(response), 200
        else:
            response = {
            'error_msg': "You cannot move in that direction.",
            }
            return jsonify(response), 500
    elif direction == "e":
        if room.exit_east_room_id:
            e_room = Room.query.filter_by(id=room.exit_east_room_id).first()
            user.location_room_id = room.exit_east_room_id
            db.session.commit()
            response = {
            'title': e_room.title,
            'description': e_room.description,
            'players': players_list,
            # 'players': player.current_room...,
            # 'items': items...
            }
            return jsonify(response), 200
        else:
            response = {
            'error_msg': "You cannot move in that direction.",
            }
            return jsonify(response), 500
    elif direction == "w":
        if room.exit_west_room_id:
            w_room = Room.query.filter_by(id=room.exit_west_room_id).first()
            user.location_room_id = room.exit_west_room_id
            db.session.commit()
            response = {
            'title': w_room.title,
            'description': w_room.description,
            'players': players_list,
            # 'items': items...
            }
            return jsonify(response), 200
        else:
            response = {
            'error_msg': "You cannot move in that direction.",
            }
            return jsonify(response), 500


@app.route('/api/adv/take/', methods=['POST'])
def take_item():
    # request item from room
    # if none return appropriate response
    #  put into player inventory
    response = {'error': "Not implemented"}
    return jsonify(response), 400


@app.route('/api/adv/drop/', methods=['POST'])
def drop_item():
    # request item from player inventory
    # if none return error
    # put into room inventory
    response = {'error': "Not implemented"}
    return jsonify(response), 400


@app.route('/api/adv/inventory/', methods=['GET'])
def inventory():
    # request items from player inventory
    response = {'error': "Not implemented"}
    return jsonify(response), 400


# @app.route('/api/adv/buy/', methods=['POST'])
# def buy_item():
#     # IMPLEMENT THIS
#     response = {'error': "Not implemented"}
#     return jsonify(response), 400


# @app.route('/api/adv/sell/', methods=['POST'])
# def sell_item():
#     # IMPLEMENT THIS
#     response = {'error': "Not implemented"}
#     return jsonify(response), 400


@app.route('/api/adv/rooms/', methods=['GET'])
def rooms():
    # IMPLEMENT THIS
    response = {'error': "Not implemented"}
    return jsonify(response), 400

@app.route("/generate")
def generate():
    rooms = test.create_world()

    for room_id, room in rooms.items():
        n_to = room.n_to.id if room.n_to else None
        s_to = room.s_to.id if room.s_to else None
        e_to = room.e_to.id if room.e_to else None
        w_to = room.w_to.id if room.w_to else None
        new_room = Room(title=room.name, description=room.description, exit_north_room_id=n_to,
                                   exit_south_room_id=s_to,
                                   exit_west_room_id=w_to, exit_east_room_id=e_to)
        try:
            db.session.add(new_room)
            db.session.commit()
        except Exception:
            print("An exception occurred",Exception)
    return {},200


# Run the program on port 5000
if __name__ == '__main__':
    app.run(port=config('PORT'))
