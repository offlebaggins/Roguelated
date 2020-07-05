import tcod

from game_messages import Message
from components.fighter import Fighter


class Appendage:
    def __init__(self, name, hp=5, grabs: bool = False, fighter: Fighter = None):
        self.name = name
        self.grabs = grabs
        self.fighter = fighter
        self.owner = None
        self.max_hp = hp
        self.hp = hp

        if self.fighter:
            self.fighter.owner = self

    def select(self):
        results = [{
            'message': Message("You ready your {0}".format(self.name))
        }]
        return results

    def take_damage(self, amount):
        results = []

        self.hp -= amount

        if self.hp <= 0:
            self.hp = 0
            results.append({'message': Message(
                'The {0}\'s {1} is mangled to a bloody pulp!'.format(self.owner.owner.name, self.name), tcod.darker_crimson)})
            self.fighter = None
            # results.append({'dead': self.owner.owner.owner});
            # results.extend(self.owner.sever())

        return results

    def heal(self, amount):
        self.hp += amount

        if self.hp > self.max_hp:
            self.hp = self.max_hp
