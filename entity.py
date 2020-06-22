import math

from render_functions import RenderOrder


class Entity:
    def __init__(self, x, y, char, color, name, blocks=False, render_order=RenderOrder.CORPSE,
                 ai=None, fighter=None, inventory=None, item=None, stairs=None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.render_order = render_order
        self.ai = ai
        self.fighter = fighter
        self.inventory = inventory
        self.item = item
        self.stairs = stairs

        if self.ai:
            self.ai.owner = self

        if self.fighter:
            self.fighter.owner = self

        if self.inventory:
            self.inventory.owner = self

        if self.item:
            self.item.owner = self

        if self.stairs:
            self.stairs.owner = self

    def move(self, dx, dy):
        # Move the entity by the given amount
        self.x += dx
        self.y += dy

    def distance(self, x, y):
        dx = x - self.x
        dy = y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)


def get_blocking_entities_at_location(entities, destination_x, destination_y):
    for entity in entities:
        if entity.blocks and entity.x == destination_x and entity.y == destination_y:
            return entity

    return None
