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

    def attack(self, target):
        results = []

        damage = self.power - target.defense

        if damage > 0:
            results.append({'message': Message('The {0} attacks the {1} for {2} damage!'.format(self.owner.name,
                                                                                                target.owner.name,
                                                                                                damage))})
            results.extend(target.take_damage(damage))
        else:
            results.append({'message': Message('The {0} attacks the {1} but deals no damage!'.format(self.owner.name,
                                                                                                     target.owner.name))})

        return results

    def take_damage(self, amount):
        results = []

        self.hp -= amount

        if self.hp <= 0:
            self.hp = 0
            results.append({'dead': self.owner})

        return results

    def heal(self, amount):
        self.hp += amount

        if self.hp > self.max_hp:
            self.hp = self.max_hp

