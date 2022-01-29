from server.database.game_session import GameSession


class GameSessions:
    def __init__(self) -> None:
        self.games:list[GameSession] = []

    def new_game(self, name:str) -> int:
        conflicting_games = self.search_games(name)
        if conflicting_games and len(list(filter(lambda g: g.name == name, conflicting_games))):
            raise NameError
        id = len(self.games)
        game = GameSession(id, name)
        self.games.append(game)
        return game.state

    def search_games(self, name:str) -> GameSession:
        return list(filter(lambda g: name in g.name, self.games))

    def list_games(self) -> GameSession:
        return self.games


    def make_move(self, game_id, turn):
        self.games[game_id].put_turn(turn)
        return self.games[game_id].get_turn_nowait()

    async def get_next_turn(self, game_id):
        return await self.games[game_id].get_turn()

    async def join_game(self, game_id:int, player_id:int):
        return await self.games[game_id].join_session(player_id)

    async def join_any_game(self, player_id:int):
        games = list(filter(lambda g: len(g._players) < 2, self.games))
        if len(games) > 0:
            return await self.join_game(games[0].game_id, player_id)
        else:
            game_id = self.new_game()
            return await self.join_game(game_id, player_id)

current_sessions = GameSessions()
