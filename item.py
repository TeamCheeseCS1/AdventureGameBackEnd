import random

class Item:
    def __init__(self, id, name):
        self.id = id
        self.name = name
class Food(Item):
    def __init__(self, id, name, buy_value):
        self.buy_value = buy_value
        self.id = id
        self.name = name
        super().__init__(self.id, self.name)
class Garbage(Item):
    def __init__(self, id, name, sell_value):
        self.sell_value = sell_value
        self.id = id
        self.name = name
        super().__init__(self.id, self.name)
# Setup so running the py file will generate a 10 x 10 grid matching our World
# size. each node should contain an ID, and a randomized list as an inventory
# create the randomizable lists of items
#Food

fud = [Food(1, 'apple', 1), Food(2, 'candy bar', 1),
    Food(3, 'pb banana sandwich', 2),Food(4, 'milkshake', 2),
    Food(5, 'chicken leg', 3), Food(6, 'cheese pizza', 5),
    Garbage(11, 'banana peel', 1), Garbage(12, 'old newspaper', 1),
    Garbage(13, 'dirty glass', 1), Garbage(14, 'plastic bottle', 1),
    Garbage(15, 'tin can', 1), Garbage(16, 'aluminum can', 2)]
