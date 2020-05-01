import eventlet 
eventlet.monkey_patch()
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
from flask_socketio import SocketIO, emit

from flask import Flask, jsonify, request, render_template, make_response
from pusher import Pusher
from decouple import config

from world import World

from models import *
from flask_sqlalchemy import SQLAlchemy

from world import test
from item import Item, Food, Garbage
import bcrypt
import random

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

socketio = SocketIO(app, cors_allowed_origins="*")
players_online_list = []

@socketio.on('logout') 
def user_leaving(user):
    players_online_list.remove(user)
    emit('player', {'data': players_online_list})

class Player(db.Model):
    __tablename__ = 'player'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)
    location_room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=True)

    def __init__(self, username, password, location_id=None):
        self.username = username
        self.password = password
        self.location_room_id = location_id

    def __repr__(self):
        return '<id {}>'.format(self.id)

class Item(db.Model):
    __tablename__ = "item"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    room_location = db.Column(db.Integer, db.ForeignKey("room.id"),nullable=True)
    
    def __init__(self, name, room_num):
        self.name = name
        self.room_location = room_num
    def __repr__(self):
        return '<id {}>'.format(self.id)

class Player_Item(db.Model):
    __tablename__ = "player_item"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player_id = db.Column(db.Integer, db.ForeignKey("player.id"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=False)


    def __init__(self, player_id, item_id):
        self.player_id = player_id
        self.item_id = item_id

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
    response.headers.add('Access-Control-Allow-Credentials', 'false')
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
    values = request.json
    required = ['username', 'password1', 'password2']
    
    if not all(k in values for k in required):
        response = {'message': "Missing Values"}
        return jsonify(response), 400
    

    username = values["username"]
    password1 = values["password1"]
    password2 = values["password2"]

    registered_users = Player.query.filter_by(username=values["username"]).first()
    print(registered_users)
    if registered_users is not None:
        response = {'message': "User by that username already exists"}
        return jsonify(response), 201
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

def get_room_items(items_list, player):
    items = []
    for i in items_list:
        if i.room_location == player.location_room_id:
            items.append(i.name)
    return items


@app.route('/api/login/', methods=['POST'])
def login():
    req = request.json
    user = Player.query.filter_by(username=req["username"]).first()
    players = Player.query.all()
    item_list = Item.query.all()

    if user and Bcrypt.check_password_hash(user.password, req["password"]):
        token = jwt.encode({'id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, 'JWT_SECRET')
        user.location_room_id = random.randint(1, 100)
        db.session.commit()
        items_result = get_room_items(item_list, user)
        fun_results = get_room_players(players, user)
        room = Room.query.filter_by(id=user.location_room_id).first()

        nsew = [room.exit_north_room_id, room.exit_south_room_id, room.exit_east_room_id, room.exit_west_room_id]
        response = {
            'username': user.username,
            'key': token.decode("ascii"),
            'id': user.id,
            'location_room_id': user.location_room_id,
            'players': fun_results,
            'room_description': room.description,
            'title': room.title,
            "nsew": nsew,
            "items": items_result,
        }
        players_online_list.append(user.username)
        socketio.emit('player', {'data': players_online_list})
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
    next_id = user.location_room_id
    room = Room.query.filter_by(id=next_id).first()
    direction = values.get('direction')
    players = Player.query.all()
    
    players_list = get_room_players(players, user)
    if direction == "n":
        if room.exit_north_room_id:       
            n_room = Room.query.filter_by(id=room.exit_north_room_id).first()
            user.location_room_id = room.exit_north_room_id
            db.session.commit()
            nsew = [n_room.exit_north_room_id, n_room.exit_south_room_id, n_room.exit_east_room_id, n_room.exit_west_room_id]
            item_list = Item.query.all()
            items_result = get_room_items(item_list, user)

            response = {
            'title': n_room.title,
            'description': n_room.description,
            'players': players_list,
            'current_location_id': user.location_room_id,
            'nsew': nsew,
            'items': items_result
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
            nsew = [s_room.exit_north_room_id, s_room.exit_south_room_id, s_room.exit_east_room_id, s_room.exit_west_room_id]
            item_list = Item.query.all()
            items_result = get_room_items(item_list, user)
            response = {
            'title': s_room.title,
            'description': s_room.description,
            'players': players_list,
            'current_location_id': user.location_room_id,
            'nsew': nsew,
            'items': items_result
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
            nsew = [e_room.exit_north_room_id, e_room.exit_south_room_id, e_room.exit_east_room_id, e_room.exit_west_room_id]
            item_list = Item.query.all()
            items_result = get_room_items(item_list, user)
            response = {
            'title': e_room.title,
            'description': e_room.description,
            'players': players_list,
            'current_location_id': user.location_room_id,
            'nsew': nsew,
            'items': items_result
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
            nsew = [w_room.exit_north_room_id, w_room.exit_south_room_id, w_room.exit_east_room_id, w_room.exit_west_room_id]
            item_list = Item.query.all()
            items_result = get_room_items(item_list, user)
            response = {
            'title': w_room.title,
            'description': w_room.description,
            'players': players_list,
            'current_location_id': user.location_room_id,
            'nsew': nsew,
            'items': items_result
            }
            return jsonify(response), 200
        else:
            response = {
            'error_msg': "You cannot move in that direction.",
            }
            return jsonify(response), 500


@app.route('/api/adv/take/', endpoint='take', methods=["POST"])
def take_item():
    values = request.json
    player_data = Player.query.filter_by(username=values["username"]).first()
    player_id = player_data.id
    current = player_data.location_room_id
    search = Item.query.filter_by(room_location=current).all()
    pick_this = Item.query.filter_by(name=values["item_name"]).first()
    if not search:
        response = {"message": "No items found"}
        return jsonify(response), 201
    for item in search:
        if item.name == pick_this.name:
            picked_id = item.id
            print(item.id)
            picked_item = Item.query.get(picked_id)
            print(picked_item.name)
            pick_up = Player_Item(player_id=player_id, item_id=picked_id)
            db.session.add(pick_up)
            picked_item.room_location = None
            db.session.commit()

            response = {
                "item": picked_item.name,
                'item_id': picked_item.id,
                'player_item_id': pick_up.id
            }
    return jsonify(response), 200


@app.route('/testcode')
def testcode():
    search_item = Item_vault.query.filter_by(location_room_id=12).first()
    x = search_item.location_room_id
    y = search_item.player_id

    search_item.location_room_id = y
    search_item.player_id = x
    db.session.commit()

    return {}




@app.route('/api/adv/drop/', endpoint='drop', methods=["POST"])
def drop_item():
    values = request.json
    Player_Item.query.filter_by(id=values["player_item_id"]).delete()
    db.session.commit()
    return {}, 200


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

@app.route("/generate/room")
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
    return {}

@app.route("/generate/item")
def generateItem():
    fud = [Food(1, 'apple', 1), Garbage(15, 'tin can', 1), Garbage(16, 'aluminum can', 2)]
    room = 1
    while room < 101:
        for x in fud:
            item = Item(name=x.name, room_num=room)
            item = Item(name=x.name, room_num=room)
            item = Item(name=x.name, room_num=room)

            db.session.add(item)

            db.session.commit()
        room += 1
    return {}



@app.route("/api/init")
def initialize():
    user = Player.query.filter_by
    

# Run the program on port 5000
if __name__ == '__main__':
    app.run(port=config('PORT'))
    socketio.run(app)