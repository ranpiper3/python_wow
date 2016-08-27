"""
This holds the classes for every kind of item in the game
"""
from buffs import Buff


class Item:
    def __init__(self, name: str, buy_price: int, sell_price: int, quest_ID: int=0):
        self.name = name
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.quest_ID = quest_ID

    def __str__(self):
        return "{} - Miscellaneous Item".format(self.name)


class Weapon(Item):
    def __init__(self, name: str, buy_price: int = 0, sell_price: int = 0, min_damage: int = 0, max_damage: int = 1):
        super().__init__(name, buy_price, sell_price)
        self.min_damage = min_damage
        self.max_damage = max_damage

    def __str__(self):
        return "{} - Weapon ({}-{} damage)".format(self.name, self.min_damage, self.max_damage)


class Potion(Item):
    """ Consumable item that gives a buff to the player"""
    def __init__(self, name: str, buy_price: int, sell_price: int,  buff: Buff, quest_ID: int=0,):
        super().__init__(name, buy_price, sell_price, quest_ID)

    def consume(self, character):
        # TODO: character.add_buff(self.buff)
        pass