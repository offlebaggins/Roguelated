import tcod
import math

from game_messages import Message
from random import randint


def heal(*args, **kwargs):
    entity = args[0]
    amount = kwargs.get('amount')

    results = []

    if entity.fighter.hp == entity.fighter.max_hp:
        results.append({'consumed': False,
                        'message': Message("The {0} is already at full health".format(entity.name),
                                           tcod.desaturated_green)
                        })
    else:
        entity.fighter.heal(amount)
        results.append({'consumed': True,
                        'message': Message("The {0}\'s wounds begin to heal".format(entity.name), tcod.green)
                        })

    return results


def cast_lighting(*args, **kwargs):
    caster = args[0]
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    maximum_range = kwargs.get('maximum_range')

    results = []

    target = None
    closest_distance = maximum_range + 1

    for entity in entities:
        if entity.fighter and entity != caster and tcod.map_is_in_fov(fov_map, entity.x, entity.y):

            distance = entity.distance_to(caster)

            if distance < closest_distance:
                target = entity
                closest_distance = distance

    if target:
        results.append({'consumed': True,
                        'message': Message(
                            'A lighting bolt fires from the {0} and strikes the {1} for {2} damage!'.format(caster.name,
                                                                                                            target.name,
                                                                                                            damage))})
        results.extend(target.fighter.take_damage(damage))
    else:
        results.append({'consumed': False,
                        'message': Message('There are no enemies in lightning bolt range!', tcod.light_blue)})
    return results


def teleport(*args, **kwargs):
    entity = args[0]
    game_map = kwargs.get('game_map')

    results = []

    found_spot = False

    while not found_spot:
        destination_x = randint(0, game_map.width - 1)
        destination_y = randint(0, game_map.height - 1)

        found_spot = not game_map.is_blocked(destination_x, destination_y)

    entity.x = destination_x
    entity.y = destination_y
    results.append({'consumed': True,
                    'message': Message("The {0} teleports to a new location!".format(entity.name), tcod.light_blue)})

    return results


def cast_fireball(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    radius = kwargs.get('radius')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not tcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({'consumed': False,
                        'message': Message('You cannot see there..', tcod.orange)})
        return results

    results.append({'consumed': True,
                    'message': Message('The fireball explodes, burning everything within {0} tiles!'.format(radius),
                                       tcod.lighter_orange)})

    for entity in entities:
        if entity.fighter and entity.distance(target_x, target_y) < radius:
            results.append({'message': Message('The {0} gets burned for {1} hit points.'.format(entity.name, damage),
                                               tcod.lighter_orange)})
            results.extend(entity.fighter.take_damage(damage))

    return results


def cast_explosion(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    game_map = kwargs.get('game_map')
    damage = kwargs.get('damage')
    radius = kwargs.get('radius')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not tcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({'consumed': False,
                        'message': Message('You cannot see there..', tcod.orange)})
        return results

    results.append({'consumed': True,
                    'message': Message('The explosion decimates everything within {0} tiles!'.format(radius),
                                       tcod.lighter_orange)})

    map_changed = False

    for x in range(game_map.width):
        for y in range(game_map.height):
            dx = x - target_x
            dy = y - target_y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance < radius:
                game_map.tiles[x][y].hollow()
                map_changed = True

    if map_changed:
        results.append({'map_changed': True})

    for entity in entities:
        if entity.fighter and entity.distance(target_x, target_y) < radius:
            results.append({'message': Message(
                'The {0} is caught in the explosion and takes {1} damage.'.format(entity.name, damage),
                tcod.lighter_orange)})
            results.extend(entity.fighter.take_damage(damage))

    return results
