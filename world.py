from room import Room
from player import Player
import random
import math
import bcrypt

class World:
    def __init__(self):
        self.starting_room = None
        self.rooms = {}
        self.players = {}
        self.create_world()
        self.password_salt = bcrypt.gensalt()

    def add_player(self, username, password1, password2):
        if password1 != password2:
            return {'error': "Passwords do not match"}
        elif len(username) <= 2:
            return {'error': "Username must be longer than 2 characters"}
        elif len(password1) <= 5:
            return {'error': "Password must be longer than 5 characters"}
        elif self.get_player_by_username(username) is not None:
            return {'error': "Username already exists"}
        password_hash = bcrypt.hashpw(password1.encode(), self.password_salt)
        player = Player(username, self.starting_room, password_hash)
        self.players[player.auth_key] = player
        return {'key': player.auth_key}

    def get_player_by_auth(self, auth_key):
        if auth_key in self.players:
            return self.players[auth_key]
        else:
            return None

    def get_player_by_username(self, username):
        for auth_key in self.players:
            if self.players[auth_key].username == username:
                return self.players[auth_key]
        return None

    def authenticate_user(self, username, password):
        user = self.get_player_by_username(username)
        if user is None:
            return None
        password_hash = bcrypt.hashpw(password.encode() ,self.password_salt)
        if user.password_hash == password_hash:
            return user
        return None

    def create_world(self):
        # UPDATE THIS:
        # Should create 100 procuedurally generated rooms
        self.rooms = {
            'outside':  Room("Outside Cave Entrance",
                             "North of you, the cave mount beckons", 1, 1, 1),

            'foyer':    Room("Foyer", """Dim light filters in from the south. Dusty
        passages run north and east.""", 2, 1, 2),

            'overlook': Room("Grand Overlook", """A steep cliff appears before you, falling
        into the darkness. Ahead to the north, a light flickers in
        the distance, but there is no way across the chasm.""", 3, 1, 3),

            'narrow':   Room("Narrow Passage", """The narrow passage bends here from west
        to north. The smell of gold permeates the air.""", 4, 2, 2),

            'treasure': Room("Treasure Chamber", """You've found the long-lost treasure
        chamber! Sadly, it has already been completely emptied by
        earlier adventurers. The only exit is to the south.""", 5, 2, 3),
        }

        # Link rooms together
        self.rooms['outside'].connect_rooms('n', self.rooms['foyer'])
        self.rooms['foyer'].connect_rooms('n', self.rooms['overlook'])
        self.rooms['foyer'].connect_rooms('e', self.rooms['narrow'])
        self.rooms['narrow'].connect_rooms('n', self.rooms['treasure'])

        self.starting_room = self.rooms['outside']




