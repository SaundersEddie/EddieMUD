
import asyncio
from time import sleep
import threading
import pytest
from telnetlib3 import open_connection
from EddieMUD.core.main import Main

@pytest.fixture(scope="module")
def server_loop():
    server_loop = asyncio.new_event_loop()
    server_loop.set_task_factory(asyncio.eager_task_factory)
    yield server_loop
    server_loop.stop()
    server_loop.close()

async def wait_for(c):
    r = await c
    return r

@pytest.fixture(scope="module")
def main(server_loop):
    main = Main()
    t = server_loop.call_soon(main.loop)
    c = main.loop()

    thread = threading.Thread(target=server_loop.run_until_complete, args=(c,))
    thread.daemon = True
    thread.start()
    # f = asyncio.run_coroutine_threadsafe(main.loop(), loop)
    while not main.running:
        print("WAITING FOR SERVER UP")
        sleep(1)
        # loop.run_until_complete(asyncio.sleep(1))
    print("YIELDING")
    yield main
    print("YIELDED")
    main.shutdown = True
    while main.running:
        print("WAITING FOR SERVER DOWN")
        sleep(1)
        # loop.run_until_complete(asyncio.sleep(1))
    # loop.call_soon_threadsafe(loop.stop)
    # loop.run_until_complete()
    # thread.join()
    # f.result()

def test_listening(server_loop, main):
    print("OPENING CONNECTION")
    client_loop = asyncio.new_event_loop()
    reader, writer = client_loop.run_until_complete(open_connection('localhost', 6023))
    print("READING", reader, writer)
    f = asyncio.run_coroutine_threadsafe(reader.read(8), client_loop)
    msg = f.result()
    assert msg == "\rName: "
    print("DONE")
