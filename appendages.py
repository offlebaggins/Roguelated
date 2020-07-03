import tcod

from game_messages import Message
from components.fighter import Fighter


class Appendage:
    def __init__(self, name, grabs: bool = False, fighter: Fighter = None):
        self.name = name
        self.grabs = grabs
        self.fighter = fighter
        self.owner = None

        if self.fighter:
            self.fighter.owner = self

    def select(self):
        results = [{
            'message': Message("You ready your {0}".format(self.name))
        }]
        return results

    def sever(self):
        results = []
        if self.owner:
            self.grabs = False
            self.fighter = None
            results.append(
                {'message': Message("The {0}'s {1} is severed.".format(self.owner.owner.name, self.name), tcod.red)})

        # self.owner = None

        return results
