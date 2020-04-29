import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request, render_template
from pusher import Pusher
from decouple import config

from room import Room
from player import Player
from world import World

from models import *
from flask_sqlalchemy import SQLAlchemy

# Look up decouple for config variables
pusher = Pusher(app_id=config('PUSHER_APP_ID'), key=config(
    'PUSHER_KEY'), secret=config('PUSHER_SECRET'), cluster=config('PUSHER_CLUSTER'))

world = World()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///game.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


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


def get_player_by_header(world, auth_header):
    if auth_header is None:
        return None

    auth_key = auth_header.split(" ")
    if auth_key[0] != "Token" or len(auth_key) != 2:
        return None

    player = world.get_player_by_auth(auth_key[1])
    return player


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

    new_user = Player(username=username, password=password1, location_id=None)
    db.session.add(new_user)
    db.session.commit()

    response = world.add_player(username, password1, password2)
    if 'error' in response:
        return jsonify(response), 500
    else:
        return jsonify(response), 200


@app.route('/')
def root():
    return "nothin"


@app.route('/api/login/', methods=['POST'])
def login():
    # IMPLEMENT THIS
    response = {'error': "Not implemented"}
    return jsonify(response), 400


@app.route('/api/adv/init/', methods=['GET'])
def init():
    player = get_player_by_header(world, request.headers.get("Authorization"))
    if player is None:
        response = {'error': "Malformed auth header"}
        return jsonify(response), 500

    response = {
        'title': player.current_room.name,
        'description': player.current_room.description,
    }
    return jsonify(response), 200


@app.route('/api/adv/move/', methods=['POST'])
def move():
    player = get_player_by_header(world, request.headers.get("Authorization"))
    if player is None:
        response = {'error': "Malformed auth header"}
        return jsonify(response), 500

    values = request.get_json()
    required = ['direction']

    if not all(k in values for k in required):
        response = {'message': "Missing Values"}
        return jsonify(response), 400

    direction = values.get('direction')
    if player.travel(direction):
        response = {
            'title': player.current_room.name,
            'description': player.current_room.description,
        }
        return jsonify(response), 200
    else:
        response = {
            'error': "You cannot move in that direction.",
        }
        return jsonify(response), 500


@app.route('/api/adv/take/', methods=['POST'])
def take_item():
    # IMPLEMENT THIS
    response = {'error': "Not implemented"}
    return jsonify(response), 400


@app.route('/api/adv/drop/', methods=['POST'])
def drop_item():
    # IMPLEMENT THIS
    response = {'error': "Not implemented"}
    return jsonify(response), 400


@app.route('/api/adv/inventory/', methods=['GET'])
def inventory():
    # IMPLEMENT THIS
    response = {'error': "Not implemented"}
    return jsonify(response), 400


@app.route('/api/adv/buy/', methods=['POST'])
def buy_item():
    # IMPLEMENT THIS
    response = {'error': "Not implemented"}
    return jsonify(response), 400


@app.route('/api/adv/sell/', methods=['POST'])
def sell_item():
    # IMPLEMENT THIS
    response = {'error': "Not implemented"}
    return jsonify(response), 400


@app.route('/api/adv/rooms/', methods=['GET'])
def rooms():
    # IMPLEMENT THIS
    response = {'error': "Not implemented"}
    return jsonify(response), 400


# Run the program on port 5000
if __name__ == '__main__':
    app.run(config('PORT'))
