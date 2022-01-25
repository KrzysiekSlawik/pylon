from fastapi import FastAPI, Depends
from common.pylon import GameState
from server.database import DBLive, DBSession, PlayerSchema
from typing import List

from server.game_session import GameSessionSchema


app = FastAPI()

database = DBSession()

db_live = DBLive()

def get_db():
    try:
        yield database
    finally:
        database.session.close()


@app.get('/player/new/{nick}')
def player_new(nick, db=Depends(get_db)):
    return db.new_player(nick)


@app.get('/game/new')
def game_new():
    return db_live.new_game()


@app.get('/game/join/{game_id}/{player_id}')
async def game_join(game_id:int,player_id:int):
    return await db_live.join_game(game_id, player_id)


@app.get('/game/join/{player_id}')
async def game_join_any(player_id:int):
    return await db_live.join_any_game(player_id)


@app.get('/player/list', response_model=List[PlayerSchema])
def player_list(db=Depends(get_db)):
    players = db.list_players()
    return list(map(lambda p: PlayerSchema(id=p.id, nick=p.nick, wins=p.wins, loses=p.loses), players))


@app.get('/game/list', response_model=List[GameSessionSchema])
def game_list():
    games = db_live.list_games()
    return list(map(lambda g: GameSessionSchema(game_id=g.game_id,
                                                players_id=g.players,
                                                game_state=g.game_state), games))

@app.post('/game/{game_id}/move')
def game_move(game_id:int):
    return db_live.make_move(game_id, [])

@app.get('/game/{game_id}/next_state')
async def game_next_state(game_id: int):
    return await db_live.get_next_turn(game_id)
