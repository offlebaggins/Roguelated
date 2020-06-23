import tcod

from game_messages import Message


class Inventory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []

    def add_item(self, item):
        results = []

        if len(self.items) >= self.capacity - 1:
            results.append({
                'item_added': None,
                'message': Message('You cannot carry anything else!')
            })
        else:
            results.append({
                'item_added': item,
                'message': Message('You pick up the {0}'.format(item.name), item.color)
            })

        self.items.append(item)

        return results

    def use(self, item_entity, **kwargs):
        results = []

        if item_entity:
            item_component = item_entity.item

            if item_component.use_function is None:
                results.append({'message': Message('The {0} cannot be used'.format(item_entity.name), tcod.yellow)})
            else:
                if item_component.targeting and not (kwargs.get('target_x') or kwargs.get('target_y')):
                    results.append({'targeting': item_entity})
                else:
                    kwargs = {**item_component.function_kwargs, **kwargs}
                    item_use_results = item_component.use_function(self.owner, **kwargs)
                    for item_use_result in item_use_results:
                        if item_use_result.get('consumed'):
                            self.remove_item(item_entity)

                    results.extend(item_use_results)
        else:
            results.append({'message': Message('You do nothing with nothing..', tcod.yellow)})

        return results

    def remove_item(self, item):
        self.items.remove(item)

    def drop_item(self, item):
        results = []

        if item:
            item.x = self.owner.x
            item.y = self.owner.y

            self.remove_item(item)
            results.append({'item_dropped': item,
                            'message': Message('You drop the {0} on the ground'.format(item.name), item.color)
                            })
        else:
            results.append({'message': Message('You drop nothing.', tcod.yellow)})

        return results
