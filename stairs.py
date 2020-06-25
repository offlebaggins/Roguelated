import tcod

from components.structure import Structure
from game_messages import Message

class Stairs(Structure):
    def __init__(self, floor):
        self.floor = floor

    def interact(self, entity):
        interact_results = []

        interact_results.append({
            'message': Message("You travel to the depths below..", tcod.dark_crimson),
            'next_floor': True
        })

        return interact_results
