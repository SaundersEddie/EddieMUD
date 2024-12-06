import pytest

from EddieMUD.core.objects import World, Area, Room, Mob, MobDefinition, Obj, ObjDefinition

@pytest.fixture
def world():
    return World()

@pytest.fixture
def area(world):
    return Area(world, 1, 'area1')

@pytest.fixture
def room(area):
    return Room(area, 1, 'room1')

@pytest.fixture
def mob_definition():
    return MobDefinition(1, 'mob1')

@pytest.fixture
def mob(room, mob_definition):
    return Mob(room, mob_definition)

def test_init_world(world):
    assert world.areas == []

def test_init_area(world, area):
    assert area.world == world
    assert area in world.areas
    assert area.rooms == []
    assert area.flags['open'] is True

def test_init_room(world, area, room):
    assert room.area == area
    assert room in area.rooms
    assert room.doors == {}
    assert room.actions == []
    assert room.objects == []
    assert room.mobs == []
    assert room.resets == []
    assert room.flags == {}

def test_init_mob(room, mob):
    assert mob.room == room
    assert mob in room.mobs
