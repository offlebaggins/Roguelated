from enum import auto, Enum


class ActionType(Enum):
    ESCAPE = auto()
    MOVEMENT = auto()
    GRAB = auto()
    TOGGLE_INVENTORY = auto()
    ACTIVATE_INVENTORY_ITEM = auto()
    DROP_INVENTORY_ITEM = auto()
    RESTART = auto()
    TARGETING = auto()
    EXECUTE = auto()
    NEW_GAME = auto()
    LOAD_GAME = auto()


class Action:
    def __init__(self, action_type: ActionType, **kwargs):
        self.action_type: ActionType = action_type
        self.kwargs = kwargs
