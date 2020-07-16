import tcod

from game_messages import Message
from components.fighter import Fighter
from components.grabber import Grabber


class Appendage:
    def __init__(self, name, hp=5, pain_severity=25, fighter: Fighter = None, grabber: Grabber = None):
        self.name = name
        self.max_hp = hp
        self.hp = hp

        self.pain_severity = pain_severity

        self.fighter = fighter
        self.grabber = grabber
        self.owner = None

        if self.fighter:
            self.fighter.owner = self
        if self.grabber:
            self.grabber.owner = self

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
                'The {0}\'s {1} is mangled to a bloody pulp!'.format(self.owner.owner.name, self.name),
                tcod.darker_crimson)})
            self.fighter = None
            if self.grabber:
                results.extend(self.grabber.drop())
                self.grabber = None
            # results.append({'dead': self.owner.owner.owner});
            # results.extend(self.owner.sever())

        if self.owner:
            results.extend(self.owner.process_pain())
        return results

    def heal(self, amount):
        self.hp += amount

        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def get_pain(self):
        return self.pain_severity * (1 - (self.hp / self.max_hp))
