#from app import db
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from app import db


class Player(db.Model):
    __tablename__ = 'player'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    location_room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=True)
    
    def __init__(self, username, password, location_id):
        self.username = username
        self.result_all = password
        self.result_no_stop_words = location_id

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

    def __init__(self, title, description, exit_north_room_id, exit_south_room_id, exit_west_room_id, exit_east_room_id):
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