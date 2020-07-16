import tcod
import random

from appendages import Appendage
from body import Body
from components.fighter import Fighter
from components.grabber import Grabber
from random_utils import random_choice_from_dict
from game_messages import Message
import json


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
