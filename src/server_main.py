from fastapi import FastAPI, Depends
from common.pylon import GameState
from server.database import DBSession, PlayerSchema
from typing import List


app = FastAPI()

database = DBSession()

def get_db():
    try:
        yield database
    finally:
        database.session.close()


@app.get('/newplayer/{nick}')
def new_player_id(nick, db = Depends(get_db)):
    return db.new_player(nick)


@app.get('/newgame')
def new_game(db = Depends(get_db)):
    return db.new_game()


@app.get('/join/{game_id}/{player_id}')
def join_game(game_id:int,player_id:int, db = Depends(get_db)):
    return db.join_game(game_id, player_id)


@app.get('/join/{player_id}')
def join_any_game(player_id:int, db = Depends(get_db)):
    return db.join_any_game(player_id)

@app.get('/list/players', response_model=List[PlayerSchema])
def list_players(db = Depends(get_db)):
    players =  db.list_players()
    print(players)
    return list(map(lambda p: PlayerSchema(id=p.id, nick=p.nick, wins=p.wins, loses=p.loses), players))

@app.get('/list/games', response_model=List[GameState])
def list_games(db = Depends(get_db)):
    return db.list_games()

@app.post('/play/{game_id}/{player_id}')
def play(game_id:int, player_id:int, game:GameState, db = Depends(get_db)):

