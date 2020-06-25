from components.structure import Structure
from entity import Entity
from game_messages import Message


class Door(Structure):
    def __init__(self, is_open: bool):
        self.open: bool = is_open
        self.owner: Entity = None

    def initialize(self, owner):
        self.owner = owner
        self.set_open(False)

    def interact(self, entity):
        interact_results = []

        if self.open:
            self.set_open(False)
            verb = "closes"
        else:
            self.set_open(True)
            verb = "opens"

        interact_results.append({
            'message': Message("The {0} {1} the door.".format(entity.name, verb))
        })
        return interact_results

    def set_open(self, is_open):
        if is_open:
            self.open = True
            self.owner.description = "It is open"
            self.owner.blocks = False
            self.owner.char = '_'
        else:
            self.open = False
            self.owner.description = "It is closed"
            self.owner.blocks = True
            self.owner.char = '+'


