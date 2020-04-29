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
