from common.messages import BadMsgResp, MoveMsgError, msg_from_json
from fastapi import (
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from server.database.game_session import GameSessionState

from tortoise.contrib.fastapi import register_tortoise

from server.database.models.user import Users, user_pydantic

from server.database.active_game_sessions import current_sessions


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["server.database.models.user"]},
    generate_schemas=True,
    add_exception_handlers=True,
)


@app.post("/player/new/{username}", response_model=user_pydantic)
async def player_new(username: str):
    """
    Create new player
    """
    user = await Users.create(username=username)
    return await user_pydantic.from_tortoise_orm(user)


@app.get("/player/list", response_model=List[user_pydantic])
async def player_list():
    """
    list players
    """
    return await user_pydantic.from_queryset(Users.all())


@app.post("/game/new", response_model=GameSessionState)
async def game_new(name: str):
    """
    Create new game and returns it's state

    - **name**: game name should be unique
    """
    try:
        return current_sessions.new_game(name)
    except NameError:
        return HTTPException(code=409, detail="game with this name already exists!")


@app.get("/game/search/{name}", response_model=List[GameSessionState])
async def search_games(name: str):
    """
    List all games that contain **name** in their names
    - **name**: substring of game name to search
    """
    return list(map(lambda g: g.state, current_sessions.search_games(name)))


@app.get("/game/list", response_model=List[GameSessionState])
def game_list():
    """
    List all games
    """
    return list(map(lambda g: g.state, current_sessions.list_games()))


@app.websocket("/game/connect")
async def connect_to_game(websocket: WebSocket, game_id: int, player_id: int = None):
    """
    Connect to game
    - **player_id** id of player that joins, if **player_id**==0 join as spectator
    - **game_id**: id of game to join
    """
    try:
        await current_sessions.connect(websocket, game_id, player_id)
    except IndexError:
        return HTTPException(code=404, detail=f"there is no game with id = {game_id}!")
    try:
        while True:
            try:
                json_msg = await websocket.receive_json()
                msg = msg_from_json(json_msg)
                await current_sessions.handle_msg(websocket, game_id, player_id, msg)
            except TypeError:
                await websocket.send_json(
                    BadMsgResp({"detail": f"unknown msg type: {json_msg}"}).to_dict()
                )
            except MoveMsgError:
                await websocket.send_json(
                    BadMsgResp({"detail": f"MoveMsg bad data: {json_msg}"}).to_dict()
                )
    except WebSocketDisconnect:
        await current_sessions.disconnect(websocket, game_id, player_id)
