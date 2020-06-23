import tcod


def initialize_fov(game_map):
    fov_map = tcod.map_new(game_map.width, game_map.height)

    for y in range(game_map.height):
        for x in range(game_map.width):
            tcod.map_set_properties(fov_map, x, y, not game_map.tiles[x][y].block_sight,
                                    not game_map.tiles[x][y].blocked)

    return fov_map


def recompute_fov(fov_map, x, y, radius, light_walls=True, algorithm=0):
    tcod.map_compute_fov(fov_map, x, y, radius, light_walls, algorithm)


def recompute_walkable(fov_map, game_map, entities, walking_entity):
    for x in range(game_map.width):
        for y in range(game_map.height):
            if game_map.is_blocked(x, y):
                fov_map.walkable[y, x] = False
            else:
                fov_map.walkable[y, x] = True

    # for entity in entities:
    #     if walking_entity != entity and entity.blocks:
    #         fov_map.walkable[entity.y, entity.x] = True



