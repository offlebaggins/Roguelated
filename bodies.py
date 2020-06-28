import tcod

from typing import List
from appendages import Appendage
from components.fighter import Fighter
from random_utils import random_choice_from_dict
from game_messages import Message


class Body:
    def __init__(self, appendages: List[Appendage]):
        self.appendages: List[Appendage] = appendages

        for appendage in appendages:
            appendage.owner = self

        if len(self.appendages) > 0:
            self.selected_appendage = self.appendages[0]

    def select_appendage(self, appendage: Appendage):
        results = []
        results.extend(appendage.select())
        self.selected_appendage = appendage

        return results

    def sever_appendage(self, appendage: Appendage):
        results = []
        self.appendages.remove(appendage)
        results.append(
            {'message': Message("The {0}'s {1} is severed off.".format(self.owner.name, appendage.name), tcod.red)})

    def get_random_appendage(self) -> Appendage:
        # TODO: Every appendage has an equal selection bias, maybe tie this to appendage size/mass?
        choices = []
        for appendage in self.appendages:
            choices.append({appendage: 1})

        return random_choice_from_dict(choices)


def get_human_body() -> Body:
    hand_fighter = Fighter(10, 3, 3)
    left_hand = Appendage("Left hand", grabs=True, fighter=hand_fighter)
    right_hand = Appendage("Right hand", grabs=True, fighter=hand_fighter)
    tail = Appendage("Tail", grabs=True, fighter=Fighter(10, 10, 10))
    appendages = [left_hand, right_hand, tail]
    return Body(appendages)
