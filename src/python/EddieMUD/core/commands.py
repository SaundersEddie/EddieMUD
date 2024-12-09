
import random
import shlex
from functools import wraps

from .objects import Room

def must_be_in_combat(func):
    @wraps(func)
    async def wrapper(client, target):
        if not client.player.is_fighting():
            return await client.send_line(f"You are not in combat.")
        return await func(client, target)
    return wrapper

def must_not_be_in_combat(func):
    @wraps(func)
    async def wrapper(client, target):
        if client.player.is_fighting():
            return await client.send_line(f"You cannot do that while in combat.")
        return await func(client, target)
    return wrapper

def must_be_standing(func):
    @wraps(func)
    async def wrapper(client, target):
        if not client.player.is_standing():
            return await client.send_line(f"You need to be standing to do that.")
        return await func(client, target)
    return wrapper

def must_be_mobile(func):
    @wraps(func)
    async def wrapper(client, target):
        if not client.player.is_mobile():
            return await client.send_line(f"You are unable to move.")
        return await func(client, target)
    return wrapper

def must_be_awake_if_targeted(func):
    @wraps(func)
    async def wrapper(client, target):
        if target and not client.player.is_awake():
            return await client.send_line(f"You must be awake to do that.")
        return await func(client, target)
    return wrapper

def must_be_awake(func):
    @wraps(func)
    async def wrapper(client, target):
        if not client.player.is_awake():
            return await client.send_line(f"You must be awake to do that.")
        return await func(client, target)
    return wrapper

def util_resolve_target(client, target):
    return None

@must_be_awake
async def do_say(client, target):
    if target:
        await client.main.ncast(client, f"You said: {target}", f"{client.player.name} said: {target}")
    else:
        await client.send_line("Say what?")

@must_be_awake
async def do_look(client, target):
    obj = util_resolve_target(client, target) if target else client.player.room
    if obj:
        await client.send_line(f"You look at: {obj}")
        if isinstance(obj, Room):
            await client.send_line(f"{obj.name}")
            await client.send_line(f"{obj.description}")
            for p in obj.players:
                if p is not client.player:
                    await client.send_line(f"{p.name} is here.")
        else:
            print(f"Unknown obj class: {obj.__class__}")
    else:
        await client.send_line(f"You don't see anything matching '{target}' here.")

@must_be_in_combat
@must_be_standing
@must_be_mobile
async def do_flee(client, target):
    if not target:
        if not client.player.room.doors:
            await client.send_line(f"There is no exit!")
            return
        target = random.choice(list(client.player.room.doors.keys()))
    if target not in client.player.room.doors:
        await client.send_line(f"There is no exit in that direction!")
        return

async def do_inventory(client, target):
   for obj in client.player.inventory:
       await client.send_line(f"{obj.definition.name}")

@must_be_awake_if_targeted
async def do_equip(client, target):
    if not target:
        for k,v in client.player.equipment.items(): # TODO: sort by standard slots
            await client.send_line(f"{k}: {v.definition.name}")
    else:
        await client.send_line("Equipping items is not yet implemented.")

@must_be_awake
async def do_unequip(client, target):
    if not target:
        await client.send_line("What do you want to unequip?")
        return
    await client.send_line("Unequipping items is not yet implemented.")

@must_be_awake
@must_be_standing
@must_be_mobile
@must_not_be_in_combat
async def do_move(client, target):
    if not target:
        await client.send_line("In which direction do you want to move?")
        return

    if target not in ["n","north","s","south","e","east","w","west","u","up","d","down"]:
        await client.send_line(f"The direction '{target}' is not a direction.")
        return

    normalized_direction = "north" if target == "n" else "south" if target == "s" else "west" if target == "w" else "east" if target == "e" else "up" if target == "u" else "down" if target == "d" else target

    normalized_directional = f"to the {normalized_direction}" if normalized_direction not in ["up","down"] else "above" if normalized_direction == "up" else "below"
    door = client.player.room.doors.get(target,None)
    if not door:
        await client.send_line(f"You see no exit {normalized_directional}.")
        return

    if door.is_closed():
        await client.send_line(f"The door {normalized_directional} is closed.")
        return

    for p in door.room_start.players:
        if p is client.player:
            await client.send_line(f"You leave {normalized_direction}.")
        else:
            await p.client.send_line(f"{client.player.name} leaves {normalized_direction}.")

    door.room_start.players.remove(client.player)
    client.player.room = door.room_end
    door.room_end.players.append(client.player)

    for p in door.room_end.players:
        if p is client.player:
            await do_look(client,"")
        else:
            opposite_direction = "north" if normalized_direction == "south" else "south" if normalized_direction == "north" else "east" if normalized_direction == "west" else "west" if normalized_direction == "east" else "down" if normalized_direction == "up" else "up"
            opposite_directional = f"the {opposite_direction}" if opposite_direction not in ["up","down"] else "above" if opposite_direction == "up" else "below"
            await p.client.send_line(f"{client.player.name} arrives from {opposite_directional}.")
