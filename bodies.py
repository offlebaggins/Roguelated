import tcod
import random
import json

from typing import List
from appendages import Appendage
from components.fighter import Fighter
from components.grabber import Grabber
from random_utils import random_choice_from_dict
from game_messages import Message


class Body:
    def __init__(self, appendages: List[Appendage], pain_tolerance: int=100):
        self.appendages: List[Appendage] = appendages

        for appendage in appendages:
            appendage.owner = self

        if len(self.appendages) > 0:
            self.selected_appendage = self.appendages[0]

        self.pain_tolerance = pain_tolerance

    def select_appendage(self, appendage: Appendage):
        results = []

        if appendage:
            results.extend(appendage.select())
            self.selected_appendage = appendage

        return results

    def use_selected_appendage(self, **kwargs):
        grabber = self.selected_appendage.grabber
        if grabber:
            return grabber.use(**kwargs)

    def get_random_fighter_appendage(self) -> Appendage:
        choices = []
        for appendage in self.appendages:
            if appendage.fighter is not None:
                choices.append(appendage)

        if len(choices) > 0:
            choice = random.choice(choices)
            return choice
        else:
            return None

    def grab_entity(self, entity):
        results = []

        grabber = self.selected_appendage.grabber

        # If selected appendage cannot grab, try to grab with next available grabber
        if grabber is None:
            for appendage in self.appendages:
                grabber = appendage.grabber
                if grabber:
                    break

        if grabber:
            results.extend(grabber.grab(entity))
        else:
            results.append({'message': Message('You have no available appendages to grab the {0}'.format(entity.name),
                                               tcod.orange)})
        return results

    def take_damage(self, amount, appendage=None):
        results = []
        if appendage is None:
            appendage = self.get_random_fighter_appendage()

        if appendage:
            results.extend(appendage.take_damage(amount))

        pain = self.get_pain()
        if pain >= self.pain_tolerance:
            results.append({'dead': self.owner})
        return results

    def get_pain(self) -> int:
        pain = 0
        for appendage in self.appendages:
            pain += appendage.get_pain()
        return pain

    def get_pain_percent(self) -> int:
        return int((self.get_pain() / self.pain_tolerance) * 100)


def get_human_body() -> Body:
    hand_attack_verbs = {
        'punches': 3,
        'scratches': 3,
        'bashes': 2,
        'pushes': 1,
        'shoves': 1
    }
    left_hand = Appendage("Left hand", hp=10, grabber=Grabber(),
                          fighter=Fighter(defense=0, power=1, attack_verbs=hand_attack_verbs))
    right_hand = Appendage("Right hand", hp=10, grabber=Grabber(),
                           fighter=Fighter(defense=0, power=1, attack_verbs=hand_attack_verbs))

    tail_attack_verbs = {
        'whips': 2,
        'thwaps': 1,
        'pokes': 1
    }
    tail = Appendage("Tail", hp=5, fighter=Fighter(defense=0, power=3, attack_verbs=tail_attack_verbs))

    thrumbus = Appendage("Thrumbus", hp=10, pain_severity=1000)
    appendages = [left_hand, right_hand, tail, thrumbus]
    body = Body(appendages, pain_tolerance=50)
    return body


def load_body() -> Body:
    with "bodies.json" as json_file:
        #TODO: SERIALIZE APPENDAGES
        return Body(**json.load(json_file))

