from fastapi import FastAPI
from common.pylon import GameState

app = FastAPI()


@app.post('/play')
def play(state:GameState):
    return state.board[0][0][0]
