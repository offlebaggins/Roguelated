import tcod

from game_messages import Message


class TileType:
    def __init__(self):
        self.owner = None

    def overlap_entity(self, entity):
        return None

    def set_owner(self, tile):
        self.owner = tile



class Lava(TileType):
    def set_owner(self, tile):
        self.owner = tile
        self.owner.light_color = tcod.red
        self.owner.dark_color = tcod.dark_red

    def overlap_entity(self, entity):
        results = []

        damage = 1

        if entity.fighter:
            results.extend(entity.fighter.take_damage(damage))
            results.append({
                'message': Message('The {0} is burned by the lava for {1} damage!'.format(entity.name, damage))
            })

        return results
