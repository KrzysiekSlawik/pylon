import queue
from typing import List

class GameSession:
    def __init__(self, game_id: int) -> None:
        self.turn_pipe = queue.Queue()
        self.join_pipe = queue.Queue()
        self.join_pipe.put(True)
        self.join_pipe.put(True)
        self.game_id = game_id
        self.players = []

    def end_turn(self) -> bool:
        self.turn_pipe.put(True)

    def get_turn(self) -> None:
        self.turn_pipe.get()

    def join_session(self, player_id) -> bool:
        try:
            self.join_pipe.get_nowait()
            self.players.append(player_id)
            return True
        except queue.Empty:
            return False

