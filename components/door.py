from components.structure import Structure
from entity import Entity
from game_messages import Message
from render_functions import RenderOrder


class Door(Structure):
    def __init__(self, is_open: bool):
        self.open: bool = is_open
        self.owner: Entity = None

    def initialize(self, owner):
        self.owner = owner
        self.set_open(False)
        self.owner.block_sight = True
        self.owner.render_order = RenderOrder.CLOSED_DOOR

    def interact(self, entity):
        interact_results = []

        if self.open:
            self.set_open(False)
            verb = "close"
        else:
            self.set_open(True)
            verb = "open"

        interact_results.append({
            'message': Message("The {0} {1}s the door.".format(entity.name, verb))
        })
        return interact_results

    def set_open(self, is_open):
        if is_open:
            self.open = True
            self.owner.description = "It is open"
            self.owner.blocks = False
            self.owner.char = '_'
            self.owner.render_order = RenderOrder.OPEN_DOOR
        else:
            self.open = False
            self.owner.description = "It is closed"
            self.owner.blocks = True
            self.owner.char = '+'
            self.owner.render_order = RenderOrder.CLOSED_DOOR


