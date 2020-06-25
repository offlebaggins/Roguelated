import tcod


def generate_path_map(game_map, entities, player):
    # Create a FOV map that has the dimensions of the map
    path_map = tcod.map_new(game_map.width, game_map.height)

    # Scan the current map each turn and set all the walls as unwalkable
    for y1 in range(game_map.height):
        for x1 in range(game_map.width):
            tcod.map_set_properties(path_map, x1, y1, not game_map.tiles[x1][y1].block_sight,
                                    not game_map.tiles[x1][y1].blocked)
    # Scan all the objects to see if there are objects that must be navigated around
    if entities:
        for entity in entities:
            if entity.blocks and entity != player:
                tcod.map_set_properties(path_map, entity.x, entity.y, True, False)

    return path_map


def add_entities_to_path_map(path_map, entities, self_entity, player):
    for entity in entities:
        if self_entity.distance_to(entity) < 2 and entity.blocks and entity != player:
            tcod.map_set_properties(path_map, entity.x, entity.y, True, False)

    return path_map
