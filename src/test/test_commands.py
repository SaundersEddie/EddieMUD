
import asyncio

import pytest

from EddieMUD.core.commands import do_move

@pytest.fixture
def mock_player(mocker):
    mock_player = mocker.MagicMock()
    mock_player.is_awake = lambda: True
    mock_player.is_fighting = lambda: False
    mock_player.is_mobile = lambda: True
    mock_player.is_standing = lambda: True
    return mock_player

@pytest.fixture
def mock_client(mocker, mock_player):
    mock_client = mocker.AsyncMock()
    mock_client.player = mock_player
    return mock_client

async def test_move_while_sleeping(mock_client):
    mock_client.player.is_awake = lambda: False
    await do_move(mock_client, "n")
    mock_client.send_line.assert_called_once_with("You must be awake to do that.")

async def test_move_while_fighting(mock_client):
    mock_client.player.is_fighting = lambda: True
    await do_move(mock_client, "n")
    mock_client.send_line.assert_called_once_with("You cannot do that while in combat.")

async def test_move_while_immobile(mock_client):
    mock_client.player.is_mobile = lambda: False
    await do_move(mock_client, "n")
    mock_client.send_line.assert_called_once_with("You are unable to move.")

async def test_move_no_target(mock_client):
    await do_move(mock_client, "")
    mock_client.send_line.assert_called_once_with("In which direction do you want to move?")

