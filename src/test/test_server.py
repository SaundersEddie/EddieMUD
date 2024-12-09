
import asyncio
from time import sleep
import subprocess
import pytest
from telnetlib3 import open_connection

@pytest.fixture(scope="module")
def loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.stop()
    loop.close()

@pytest.fixture(scope="module")
def server():
    p = subprocess.Popen(["python","-m","EddieMUD.core.main"])
    # wait for server up...
    sleep(5)
    yield p
    p.kill()

def test_listening(loop, server):
    async def _test_listening(loop, server):
        reader, writer = await open_connection('localhost', 6023)
        msg = await reader.read(8)
        assert msg == "\rName: "

    loop.run_until_complete(_test_listening(loop, server))
    # reader, writer = loop.run_until_complete(open_connection('localhost', 6023))
    # msg = loop.run_until_complete(reader.read(8))
    # assert msg == "\rName: "
