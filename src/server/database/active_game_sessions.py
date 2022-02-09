from common.messages import Msg
from fastapi import WebSocket
from server.database.game_session import GameSession, GameSessionState


class GameSessionsManager:
    """
    Proxy in game session communication
    """
    def __init__(self) -> None:
        self.games: list[GameSession] = []

    def new_game(self, name: str) -> GameSessionState:
        """
        raises NameError if there is already game with the same name
        """
        conflicting_games = self.search_games(name)
        if conflicting_games and len(
            list(filter(lambda g: g.name == name, conflicting_games))
        ):
            raise NameError
        id = len(self.games)
        game = GameSession(id, name)
        self.games.append(game)
        return game.state

    def search_games(self, name: str) -> GameSession:
        return list(filter(lambda g: name in g.name, self.games))

    def list_games(self) -> GameSession:
        return self.games

    async def connect(self, websocket: WebSocket, game_id: int, player_id: int):
        """
        Throws IndexError if **game_id** doesnt corespond to any game
        """
        await self.games[game_id].connect(websocket, player_id)

    async def disconnect(self, websocket: WebSocket, game_id: int, player_id: int):
        """
        Throws IndexError if **game_id** doesnt corespond to any game
        """
        await self.games[game_id].disconnect(websocket, player_id)

    async def handle_msg(self, websocket: WebSocket, game_id: int, player_id: int, msg: Msg):
        """
        Throws IndexError if **game_id** doesnt corespond to any game
        """
        await self.games[game_id].handle_msg(websocket, player_id, msg)


current_sessions = GameSessionsManager()
