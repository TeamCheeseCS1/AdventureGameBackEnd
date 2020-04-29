import os
from app import db
from models import Players

PLAYERS = [
    {'username': 'Ethan', 'password': 'Password123!'},
    {'username': 'Dan', 'password': 'Security123!'},
    {'username': 'Matt', 'password': 'SuperSecure456!'}
]

for user in PLAYERS:
    p = Players(username=user['username'], password=user['password'])
    db.session.add(p)
db.session.commit()