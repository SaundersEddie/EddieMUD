"""A simple telnetlib3 server"""

import asyncio
import inspect
from telnetlib3 import create_server
from telnetlib3.telopt import WONT, ECHO, SGA
from . import commands
from .objects import Area, Door, Room, Player, MobDefinition, ObjDefinition, Obj, World
import json5
import glob
import duckdb

class Client:
    def __init__(self, main, reader, writer):
        self.main = main
        self.reader = reader
        self.writer = writer
        self.connected = False
        self.player = None
    async def loop(self):
        self.writer.write(f"\rName: ")
        await self.writer.drain()
        name = await self.reader.readline()
        name = name.strip()
        if not name:
            await self.send_line("No name entered. Goodbye.")
        else:
            await self.send_line(f"Welcome, {name}.")
        # TODO: check name not already taken / password
        self.connected = True
        # name, description, definition, inventory, equipment, stats, flags...
        self.player = Player(self, self.main.start_room, name, "human fighter", self.main.mob_definitions[0], [Obj(next((o for o in self.main.obj_definitions if o.name == 'small canvas bag')))],{'right_hand':Obj(next((o for o in self.main.obj_definitions if o.name == 'iron longsword')))},{})
        for p in self.player.room.players:
            if p is not self.player:
                await p.client.send_line(f"{self.player.name} appears out of the void.")
        await commands.do_look(self, "")
        while self.connected:
            msg = await self.reader.readline()
            if msg == "":
                self.connected = False
                self.player.room.players.remove(self.player)
                for p in self.player.room.players:
                    if p is not self.player:
                        await p.client.send_line(f"{self.player.name} disappears though you did not see him leave.")
                self.reader.feed_eof()
                self.writer.close()
                return
            msg = msg.strip()
            await self.handle(msg)

    async def handle(self, msg):
        if msg in ["n","north","s","south","e","east","w","west","u","up","d","down"]:
            msg = "move " + msg
        elif msg.startswith("'"):
            msg = "say " + msg[1:]
        words = msg.split(" ", 1)
        cmd = words[0].strip()
        target = words[1].strip() if len(words) > 1 else ""
        c = self.main.commands_table.get(cmd)
        if c is None:
            await self.send_line(f"No such command: {cmd}")
        else:
            await c(self, target)

    async def send_line(self, msg):
        self.writer.write(f"\r{msg}\r\n")
        await self.writer.drain()

class Main:
    def __init__(self):
        self.running = False
        self.shutdown = False
        self.server = None
        self.clients = []
        self.commands_table = {}
        self.world = World()

        self.obj_definitions = []
        obj_definitions_q = duckdb.read_json('./data/objects/*.json')
        for obj_def_tuple in obj_definitions_q.fetchall():
            print("Loading object definition:", obj_def_tuple)
            obj_def = ObjDefinition(obj_def_tuple[0], obj_def_tuple[1])
            self.obj_definitions.append(obj_def)
        for obj_definition in self.obj_definitions:
            print("loaded:", obj_definition.name)
        self.mob_definitions = []
        mob_definitions_q = duckdb.read_json('./data/mobs/*.json')
        for mob_def_tuple in mob_definitions_q.fetchall():
            print("Loading mob definition:", mob_def_tuple)
            mob_def = MobDefinition(mob_def_tuple[0], mob_def_tuple[1])
            self.mob_definitions.append(mob_def)

        area_paths = glob.glob("./data/areas/*.json5")
        for area_path in area_paths:
            print("Loading area definition:", area_path)
            area_data = json5.load(open(area_path))
            area = Area(self.world, area_data["id"], area_data['name'], area_data.get('description','No description.'))
            door_data = []
            for r in area_data.get("rooms", []):
                room = Room(area, r["id"], r["name"], **r.get("flags", {}))
                if "doors" in r:
                    door_data.append({'room':room, 'doors':r["doors"]})
            for d in door_data:
                for k, v in d['doors'].items():
                    d['room'].doors[k] = Door(d['room'], next((r for r in area.rooms if r.id == v["to"])), **v.get("flags",{}))
        self.start_room = self.world.areas[0].rooms[0]
        # self.limbo

        functions = inspect.getmembers(commands, inspect.iscoroutinefunction)
        for name, f in functions:
            if name.startswith("do_"):
                self.commands_table[name[3:]] = f

    async def shell(self, reader, writer):
        print(f"shell: {reader}, {writer}")
        writer.iac(WONT, ECHO)
        writer.iac(WONT, SGA)
        client = Client(self, reader, writer)
        self.clients.append(client)
        await client.loop()

    async def loop(self):
        print("Main running...")
        self.running = True
        self.server = await create_server(port=6023, shell=self.shell)
        while not self.shutdown:
            await asyncio.sleep(1)
            await self.broadcast("TICK!")
        self.running = False
        asyncio.get_event_loop().run_until_complete(self.server.wait_closed())
        print("Main exiting...")

    async def broadcast(self, msg):
        for c in [c for c in self.clients if c.connected is True]:
            await c.send_line(msg)

    async def ncast(self, client, client_msg, others_msg):
        for c in [c for c in self.clients if c.connected is True and c is not client]:
            await c.send_line(others_msg)
        await client.send_line(client_msg)

if __name__=="__main__":
    main = Main()
    asyncio.get_event_loop().run_until_complete(main.loop())
