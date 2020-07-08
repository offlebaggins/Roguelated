import tcod


class BasicMonster:

    def __init__(self, fov_radius, max_stamina=2, move_cost=2):
        self.fov_radius = fov_radius
        self.max_stamina = max_stamina
        self.stamina = max_stamina
        self.move_cost = move_cost

    def take_turn(self, player, fov_map, game_map, entities, path_map):
        results = []

        if self.stamina < self.max_stamina:
            self.stamina += 1

        visible = tcod.map_is_in_fov(fov_map, self.owner.x, self.owner.y)

        # if visible:
        if self.owner.distance_to(player) >= 2:
            if self.stamina > 0:
                move_results = self.owner.move_to(player, game_map, entities, path_map, player)
                results.extend(move_results)
                self.stamina -= self.move_cost
        elif self.owner.body:
            appendage = self.owner.body.get_random_fighter_appendage()
            if appendage:
                attack_results = appendage.fighter.attack_entity(player)
                results.extend(attack_results)
            else:
                # TODO: make ai run away from player if they have no 'fighter' appendages
                pass

        return results
