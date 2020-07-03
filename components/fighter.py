import tcod

from game_messages import Message


class Fighter:
    def __init__(self, hp, defense, power):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.targeting_item = None
        self.targeting_radius = 3
        self.target_x = 0
        self.target_y = 0
        self.owner = None

    def attack_entity(self, target_entity):
        results = []

        target_appendage = None

        if target_entity.body:
            target_appendage = target_entity.body.get_random_fighter_appendage()

        if target_appendage:
            if target_appendage.fighter:
                target_fighter = target_appendage.fighter
                damage = self.power - target_fighter.defense

                if damage > 0:
                    results.append({'message': Message(
                        'The {0} attacks the {1}\'s {2} '
                        'with their {3} for {4} damage!'.format(self.owner.owner.owner.name,
                                                                target_fighter.owner.owner.owner.name,
                                                                target_fighter.owner.name,
                                                                self.owner.name,
                                                                damage))})
                    results.extend(target_fighter.take_damage(damage))
                else:
                    results.append(
                        {'message': Message('The {0} attacks the {1}\'s {2} with their {3} but deals no damage!'.format(
                            self.owner.owner.owner.name, target_fighter.owner.owner.owner.name,
                            target_fighter.owner.name, self.owner.name))})
            else:
                results.extend(target_appendage.sever())
        else:
            results.append({'message': Message('The {0} swings at the {1} with their {2} but misses!'.format(
                self.owner.owner.owner.name, target_entity.name, self.owner.name))})
        return results

    def take_damage(self, amount):
        results = []

        self.hp -= amount

        if self.hp <= 0:
            self.hp = 0
            results.append({'message': Message('The {0}\'s {1} is mangled to a bloody pulp!'.format(self.owner.owner.owner.name, self.owner.name), tcod.darker_crimson)})
            results.append({'dead': self.owner.owner.owner});
            # results.extend(self.owner.sever())

        return results

    def heal(self, amount):
        self.hp += amount

        if self.hp > self.max_hp:
            self.hp = self.max_hp
