from fastapi import FastAPI, Depends
from common.pylon import GameState
from typing import List

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
def game_new(name:str):
    current_sessions.new_game()

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
