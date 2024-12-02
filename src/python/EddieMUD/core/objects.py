
class Area:
    def __init__(self, world, id, name, description=None, **flags):
        self.world = world
        self.world.areas.append(self)
        self.id = id
        self.name = name
        self.description = description
        self.flags = {"open":True}
        for k,v in flags.items():
            self.flags[k] = v
        self.rooms = []

class Door:
    # closed = False
    # closable = False
    # openable = False
    def __init__(self, room_start, room_end, **flags): # closed=False, closable=False, openable=False):
        self.flags = {"closed":False, "closable":False, "openable":False}
        self.room_start = room_start
        self.room_end = room_end
        for k,v in flags.items():
            self.flags[k] = v
        # self.closed = closed
        # self.closable = closable
        # self.openable = openable
    def is_closed(self):
        return self.flags["closed"]

class Room:
    def __init__(self, area, id, name, description=None, **flags):
        self.area = area
        self.area.rooms.append(self)
        self.id = id
        self.name = name
        self.description = description
        self.flags = {}
        for k, v in flags.items():
            self.flags[k] = v
        self.players = []
        self.mobs = []
        self.objects = []
        self.doors = {}
        self.actions = []
        self.resets = []

class MobDefinition:
    def __init__(self, name):
        self.name = name
        self.flags = {}

class Mob:
    def __init__(self, definition, name=None, **flags):
        self.definition = definition
        self.name = name
        self.flags = dict(definition.flags)
        for k,v in flags.items():
            self.flags[k] = v

class ObjDefinition:
    def __init__(self, name):
        self.name = name
        self.flags = {}

class Obj:
    def __init__(self, definition, name=None, **flags):
        self.definition = definition
        self.name = name
        self.flags = dict(definition.flags)
        for k,v in flags.items():
            self.flags[k] = v

class Player:
    def __init__(self, client, room, name, description, definition, inventory, equipment, stats, **flags):
        self.client = client
        self.room = room
        room.players.append(self)
        self.name = name
        self.description = description
        self.definition = definition
        self.inventory = list(inventory)
        self.equipment = dict(equipment)
        self.stats = dict(stats)
        self.flags = dict(flags)
    def is_fighting(self):
        return False
    def is_mobile(self):
        return True
    def is_awake(self):
        return True
    def is_standing(self):
        return True

