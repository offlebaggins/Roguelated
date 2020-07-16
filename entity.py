import tcod
import math

from render_functions import RenderOrder
from game_messages import Message
from components.inventory import Inventory
from components.item import Item
from components.structure import Structure
from typing import List
from path_functions import add_entities_to_path_map
from body import Body


class Entity:
    def __init__(self, x, y, char, color, name, blocks=False, render_order: RenderOrder = RenderOrder.CORPSE,
                 ai=None, body: Body = None, inventory: Inventory = None, item: Item = None,
                 structure: Structure = None, description=None, block_sight=False):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.render_order: RenderOrder = render_order
        self.ai = ai
        self.body: Body = body
        self.inventory: Inventory = inventory
        self.item: Item = item
        self.structure: Structure = structure
        self.description = description

        if self.ai:
            self.ai.owner = self

        if self.inventory:
            self.inventory.owner = self

        if self.item:
            self.item.owner = self

        if self.structure:
            self.structure.initialize(self)

        if self.body:
            self.body.owner = self

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

    def move_towards(self, target_x, target_y, game_map, entities):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        if not (game_map.is_blocked(self.x + dx, self.y + dy) or
                get_blocking_entities_at_location(entities, self.x + dx, self.y + dy)):
            self.move(dx, dy)

    def move_to(self, target, game_map, entities, tile_map, player):
        move_results = []

        path_map = tile_map

        add_entities_to_path_map(path_map, entities, self, player)

        tcod.map_set_properties(path_map, self.x, self.y, True, True)

        # Allocate a A* path
        my_path = tcod.path_new_using_map(path_map, 1.41)

        # Compute the path between self's coordinates and the target's coordinates
        tcod.path_compute(my_path, self.x, self.y, target.x, target.y)

        if not tcod.path_is_empty(my_path) and tcod.path_size(my_path) < 25:
            # Find the next coordinates in the computed full path
            x, y = tcod.path_walk(my_path, True)
            if x or y:
                # Set self's coordinates to the next path tile
                self.x = x
                self.y = y
        else:
            self.move_towards(target.x, target.y, game_map, entities)

        tcod.map_set_properties(path_map, self.x, self.y, True, False)

        tcod.path_delete(my_path)

        # Interact with landed on tile
        move_results.extend(game_map.tiles[self.x][self.y].overlap_entity(self))

        return move_results

    def get_description(self):
        results = []

        if self.description:
            results.append({
                'message': Message("You examine the {0}. {1}".format(self.name, self.description), self.color)
            })
        else:
            results.append({
                'message': Message("You examine the {0}. It is indescribable.".format(self.name), self.color)
            })

        return results


def get_blocking_entities_at_location(entities, destination_x, destination_y) -> Entity:
    for entity in entities:
        if entity.blocks and entity.x == destination_x and entity.y == destination_y:
            return entity

    return


def get_entities_at_location(entities, destination_x, destination_y) -> List[Entity]:
    result = []
    for entity in entities:
        if entity.x == destination_x and entity.y == destination_y:
            result.append(entity)

    return result
