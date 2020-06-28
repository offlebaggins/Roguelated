import tcod

from typing import List
from random import randint, random
from math import sin, cos

class AnimationCharacter:
    def __init__(self, x: int, y: int, char, color):
        self.x, self.y = x, y
        self.char = char
        self.color = color

class AnimationFrame:
    def __init__(self, characters = List[AnimationCharacter]):
        self.characters = characters

class Animation:
    def __init__(self, frames: List[AnimationFrame], current_frame=0):
        self.frames = frames
        self.current_frame = current_frame


class Animator:
    def __init__(self, animations: List[Animation]):
        self.animations = animations

    def advance_frame(self):
        for animation in self.animations:
            animation.current_frame = animation.current_frame + 1
            if animation.current_frame > len(animation.frames) - 1:
                self.animations.remove(animation)


def add_explosion_animation(animator: Animator, x: int, y: int, radius: int):
    frames = []
    characters = []

    frame_number = 0
    for frame in range(radius):

        for i in range(7):
            _x = x
            _y = y
            color = tcod.orange
            characters.append(AnimationCharacter(_x, _y, 'X', color))
        frames.append(AnimationFrame(characters))
        frame_number += 1
    animation = Animation(frames)
    animator.animations.append(animation)
