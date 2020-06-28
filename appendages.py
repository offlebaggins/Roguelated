from game_messages import Message
from components.fighter import Fighter


class Appendage:
    def __init__(self, name, grabs: bool = False, fighter: Fighter = None):
        self.name = name
        self.grabs = grabs
        self.fighter = fighter

        if self.fighter:
            self.fighter.owner = self

    def select(self):
        results = [{
            'message': Message("You ready your {0}".format(self.name))
        }]
        return results
