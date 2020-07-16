import json
import random

from appendages import Appendage
from game_messages import Message
from typing import List


class Body:
    def __init__(self, appendages: List[Appendage], pain_tolerance: int = 100):
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

        results.extend(self.process_pain())
        return results

    def process_pain(self):
        results = []

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

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


def load_body() -> Body:
    with "bodies.json" as json_file:
        # TODO: SERIALIZE APPENDAGES
        return Body(**json.load(json_file))