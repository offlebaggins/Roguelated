import tcod
import random

from game_messages import Message


class Fighter:
    def __init__(self, defense, power, attack_verbs={'attacks': 1}):
        self.defense = defense
        self.power = power
        self.targeting_item = None
        self.targeting_radius = 3
        self.target_x = 0
        self.target_y = 0
        self.owner = None
        self.attack_verbs = attack_verbs

    def attack_entity(self, target_entity):
        results = []

        target_appendage = None

        if target_entity.body:
            target_appendage = target_entity.body.get_random_fighter_appendage()

        if target_appendage:
            results.extend(self.attack_appendage(target_appendage))
        # else:
        #     results.append({'message': Message('The {0} swings at the {1} with their {2} but misses!'.format(
        #         self.owner.owner.owner.name, target_entity.name, self.owner.name))})
        return results

    def attack_appendage(self, target_appendage):
        results = []
        if target_appendage.fighter:
            target_fighter = target_appendage.fighter
            attack_verb = random.choice(list(self.attack_verbs))

            damage = self.attack_verbs.get(attack_verb) - target_fighter.defense

            if damage > 0:
                attacker = self.owner.owner.owner
                message_string = 'The {0} {1} the {2}\'s {3} with their {4} for {5} damage!'.format(
                    attacker.name,
                    attack_verb,
                    target_fighter.owner.owner.owner.name,
                    target_fighter.owner.name,
                    self.owner.name,
                    damage)
                color = tcod.white if attacker.name == "Player" else tcod.red
                results.append({'message': Message(message_string, color)})
                results.extend(target_appendage.take_damage(damage))
            else:
                results.append(
                    {'message': Message('The {0} attacks the {1}\'s {2} with their {3} but deals no damage!'.format(
                        self.owner.owner.owner.name, target_fighter.owner.owner.owner.name,
                        target_fighter.owner.name, self.owner.name))})

        return results
