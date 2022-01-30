from common.messages import BadMsgResp, MoveMsgError, msg_from_json
from fastapi import FastAPI, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from common.pylos import GameState
from typing import List
from server.database.game_session import GameSession, GameSessionState

from tortoise.contrib.fastapi import (
    HTTPNotFoundError,
    register_tortoise
)

from server.database.models.user import (
    Users,
    user_pydantic
)

from server.database.active_game_sessions import (
    current_sessions
)

import logging
import logging.config

logger = logging.getLogger(__name__)


app = FastAPI()

register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["server.database.models.user"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

@app.post('/player/new/{username}', response_model=user_pydantic)
async def player_new(username:str):
    user = await Users.create(username=username)
    return await user_pydantic.from_tortoise_orm(user)

@app.get('/player/list', response_model=List[user_pydantic])
async def player_list():
    return await user_pydantic.from_queryset(Users.all())

@app.post('/game/new')
async def game_new(name:str):
    try:
        return current_sessions.new_game(name)
    except NameError:
        return HTTPException(code=409, detail="game with this name already exists!")

@app.get('/game/search/{name}', response_model=List[GameSessionState])
async def search_games(name:str):
    return list(map(lambda g: g.state, current_sessions.search_games(name)))


@app.post('/game/join/{game_id}/{player_id}')
async def game_join(game_id:int, player_id:int):
    pass

@app.post('/game/join/{player_id}')
async def game_join_any(player_id:int):
    pass

@app.get('/game/list')
def game_list():
    pass

@app.post('/game/move')
def game_move(game_id:int, player_id:int):
    pass

@app.get('/game/move')
async def game_next_state(game_id: int):
    pass

@app.websocket('/game/connect')
async def connect_to_game(websocket: WebSocket, game_id:int, player_id:int = None):
    await current_sessions.connect(websocket, game_id, player_id)
    try:
        while True:
            try:
                json_msg = await websocket.receive_json()
                msg = msg_from_json(json_msg)
                await current_sessions.handle_msg(websocket, game_id, player_id, msg)
            except TypeError:
                await websocket.send_json(
                    BadMsgResp({'detail': f'unknown msg type: {json_msg}'}).to_json()
                )
            except MoveMsgError:
                await websocket.send_json(
                    BadMsgResp({'detail': f'MoveMsg bad data: {json_msg}'}).to_json()
                )
    except WebSocketDisconnect:
        current_sessions.disconnect(websocket, game_id, player_id)

