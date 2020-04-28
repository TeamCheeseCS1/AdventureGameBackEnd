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

# Look up decouple for config variables
pusher = Pusher(app_id=config('PUSHER_APP_ID'), key=config('PUSHER_KEY'), secret=config('PUSHER_SECRET'), cluster=config('PUSHER_CLUSTER'))

world = World()

app = Flask(__name__)

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
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
    app.run(host='0.0.0.0', port=5000)
