import tcod

from game_messages import Message


class Grabber:
    def __init__(self):
        self.grabbed_entity = None

    def grab(self, entity):
        results = []
        if self.grabbed_entity is None:
            self.grabbed_entity = entity
            results.append({
                'message': Message(
                    'The {0} grabs the {1} with their {2}'.format(self.owner.owner.owner.name, entity.name,
                                                                  self.owner.name)),
                'item_added': entity
            })
        else:
            results.append({
                'message': Message("The {0} tries to grab the {1} with their {2} but is already holding the {3}".format(
                    self.owner.owner.owner.name, entity.name, self.owner.name, self.grabbed_entity.name
                ))
            })

        return results

    def use(self, **kwargs):
        results = []

        if self.grabbed_entity:
            item_component = self.grabbed_entity.item

            if item_component.use_function is None:
                results.append({'message': Message('The {0} cannot be used'.format(self.grabbed_entity.name), tcod.yellow)})
            else:
                if item_component.targeting and not (kwargs.get('target_x') or kwargs.get('target_y')):
                    results.append({'targeting': self.grabbed_entity})
                else:
                    kwargs = {**item_component.function_kwargs, **kwargs}
                    item_use_results = item_component.use_function(self.owner.owner.owner, **kwargs)
                    for item_use_result in item_use_results:
                        if item_use_result.get('consumed'):
                            self.grabbed_entity = None

                    results.extend(item_use_results)
        else:
            results.append({'message': Message('You do nothing with nothing..', tcod.yellow)})

        return results

    def drop(self):
        results = []

        entity = self.grabbed_entity
        if entity:
            entity.x = self.owner.owner.owner.x
            entity.y = self.owner.owner.owner.y
            results.append({
                'item_dropped': entity,
                'message': Message("The {0} drops the {1}.".format(self.owner.owner.owner.name, entity.name))
            })
            self.grabbed_entity = None

        return results
