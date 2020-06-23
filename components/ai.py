import tcod
import numpy as np
import math

from fov_functions import recompute_fov
from entity import get_blocking_entities_at_location


class BasicMonster:

    def __init__(self, fov_radius, max_stamina=2, move_cost=2):
        self.fov_radius = fov_radius
        self.max_stamina = max_stamina
        self.stamina = max_stamina
        self.move_cost = move_cost

    def take_turn(self, player, fov_map, game_map, entities):
        results = []

        if self.stamina < self.max_stamina:
            self.stamina += 1

        visible = tcod.map_is_in_fov(fov_map, self.owner.x, self.owner.y)

        if visible:
            if self.owner.distance_to(player) >= 2:
                if self.stamina > 0:
                    self.owner.move_to(player, game_map, entities)
                    self.stamina -= self.move_cost
            elif player.fighter.hp > 0:
                attack_results = self.owner.fighter.attack(player.fighter)
                results.extend(attack_results)

        return results