import os
import shelve


def save_game(player, entities, animator, turn_count, game_map, message_log, game_state):
    with shelve.open('savegame') as data_file:
        data_file['player_index'] = entities.index(player)
        data_file['entities'] = entities
        data_file['animator'] = animator
        data_file['turn_count'] = turn_count
        data_file['game_map'] = game_map
        data_file['message_log'] = message_log
        data_file['game_state'] = game_state


def load_game():
    if not os.path.isfile('savegame.db'):
        return FileNotFoundError

    with shelve.open('savegame') as data_file:
        player_index = data_file['player_index']
        entities = data_file['entities']
        animator = data_file['animator']
        turn_count = data_file['turn_count']
        game_map = data_file['game_map']
        message_log = data_file['message_log']
        game_state = data_file['game_state']

    player = entities[player_index]

    return player, entities, animator, turn_count, game_map, message_log, game_state
