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
        #build 100 rooms in 10 x 10 grid
        # each room has an id, exits, a description, x and y position
        desc = ["A steep cliff appears before you, falling into the darkness",
            "Children are laughing playing in piles of rubbish",
            "It smells like Satan's bathroom here",
            "You see piles of refuse as far as the eye can see",
            """There are mountains of trash as far as you can see, and humid air burns your nostrils""",
            """It's dark and musty here, and now God has abandoned you""",
            """All around you are wads of used tissues - in the distance you hear yodeling""",
            """Waste surrounds you as you sink neck-deep into filth"""]
        names =["Central Park", "Abandoned Alley", "Central Playground",
            "Hospital","School", "Seedy motel", "Truck stop bathroom",
            "Confession booth","Your uncle Steve's basement","Sommerton Beach",
            "Jonestown Lawn"]
        room_id = 0
        #build all rooms with names and descriptions

        self.rooms = {str(x):Room(names[random.randint(0,len(names) -1)], desc[random.randint(0, len(desc) - 1)], x) for x in range(1, 101)}
        #for each position on a 10 x 10 grid
        for y in range(10):
            for x in range(10):
                room_id +=1
                #add position information to each room
                self.rooms[str(room_id)].x = x
                self.rooms[str(room_id)].y = y
                #connect rooms
                #west
                if x > 0:
                    self.rooms[str(room_id)].connect_rooms('w', self.rooms[str(room_id - 1)])
                #east
                if x < 9:
                    self.rooms[str(room_id)].connect_rooms('e', self.rooms[str(room_id + 1)])
                #north
                if y > 0:
                    self.rooms[str(room_id)].connect_rooms('s', self.rooms[str(room_id - 10)])
                #south
                if y < 9:
                    self.rooms[str(room_id)].connect_rooms('n', self.rooms[str(room_id + 10)])

                # # testing Output code
                # print(self.rooms[str(room_id)].id, self.rooms[str(room_id)].name,
                #     "'", self.rooms[str(room_id)].description, "'",
                #     '\n North:', self.rooms[str(room_id)].n_to, '\nSouth:',
                #     self.rooms[str(room_id)].s_to, '\nEast:',
                #     self.rooms[str(room_id)].e_to, '\nWest:', self.rooms[str(room_id)].w_to,
                #     '\nx:', self.rooms[str(room_id)].x, 'y:', self.rooms[str(room_id)].y)

        self.starting_room = self.rooms[str(random.randint(1, 100))]
        return self.rooms
test = World()
