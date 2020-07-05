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
