import tcod

from fov_functions import recompute_fov


class BasicMonster:

    def __init__(self, fov_radius, max_stamina=2, move_cost=2):
        self.fov_radius = fov_radius
        self.max_stamina = max_stamina
        self.stamina = max_stamina
        self.move_cost = move_cost

    def take_turn(self, player, fov_map, path_map, game_map):
        results = []

        if self.stamina < self.max_stamina:
            self.stamina += 1

        visible = tcod.map_is_in_fov(fov_map, self.owner.x, self.owner.y)

        if visible:
            if self.owner.distance_to(player) >= 2:
                self.move_to(player.x, player.y, path_map)
            elif player.fighter.hp > 0:
                attack_results = self.owner.fighter.attack(player.fighter)
                results.extend(attack_results)

        return results

    def move_to(self, x, y, path_map):

        # Movement
        if self.stamina >= self.move_cost:
            astar = tcod.path.AStar(path_map)
            path = astar.get_path(self.owner.x, self.owner.y, x, y)

            if len(path) > 0:
                self.owner.x = path[0][0]
                self.owner.y = path[0][1]
                self.stamina -= self.move_cost

