import tcod
import random

from typing import List
from appendages import Appendage
from components.fighter import Fighter
from random_utils import random_choice_from_dict
from game_messages import Message


class Body:
    def __init__(self, appendages: List[Appendage], max_hp):
        self.appendages: List[Appendage] = appendages

        for appendage in appendages:
            appendage.owner = self

        if len(self.appendages) > 0:
            self.selected_appendage = self.appendages[0]

        self.hp = max_hp
        self.max_hp = max_hp

    def select_appendage(self, appendage: Appendage):
        results = []

        if appendage:
            results.extend(appendage.select())
            self.selected_appendage = appendage

        return results

    def get_random_fighter_appendage(self) -> Appendage:
        choices = []
        for appendage in self.appendages:
            if appendage.fighter is not None:
                choices.append(appendage)
        choice = random.choice(choices)
        return choice



def get_human_body() -> Body:
    left_hand = Appendage("Left hand", grabs=True, fighter=Fighter(hp=10, defense=0, power=1))
    right_hand = Appendage("Right hand", grabs=True, fighter=Fighter(hp=10, defense=0, power=1))
    tail = Appendage("Tail", grabs=True, fighter=Fighter(hp=5, defense=0, power=3))
    appendages = [left_hand, right_hand, tail]
    return Body(appendages, 100)

def get_god_body() -> Body:
    left_hand = Appendage("Left hand", grabs=True, fighter=Fighter(hp=100, defense=100, power=100))
    right_hand = Appendage("Right hand", grabs=True, fighter=Fighter(hp=100, defense=100, power=100))
    tail = Appendage("Tail", grabs=True, fighter=Fighter(hp=100, defense=100, power=100))
    appendages = [left_hand, right_hand, tail]
    return Body(appendages, 100)
