from time import sleep
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from server.game_session import GameSession

Base = declarative_base()


class Player(Base):
    __tablename__ = 'Player'
    id = Column(Integer, primary_key=True)
    nick = Column(String(255), nullable=False)
    wins = Column(Integer)
    loses = Column(Integer)


class PlayerSchema(BaseModel):
    id: int
    nick: str
    wins: int
    loses: int


class DBSession:
    def __init__(self) -> None:
        self.__create_db()
        self.session = self.__my_session()

    def __create_db(self):
        engine = create_engine('sqlite:///server.db', echo=False)
        Base.metadata.create_all(engine)

    def __my_session(self):
        engine = create_engine('sqlite:///server.db', echo=False)
        Session = sessionmaker(bind=engine)
        return Session()

    def get_player(self, id:int) -> Player:
        return self.session.query(Player).get(id)

    def new_player(self, nick:str) -> int:
        player = Player(nick=nick, wins=0, loses=0)
        self.session.add(player)
        self.session.commit()
        return player.id


    def list_players(self):
        return self.session.query(Player).all()


class DBLive:
    def __init__(self) -> None:
        self.games:list[GameSession] = []

    def make_move(self, game_id, turn):
        self.games[game_id].put_turn(turn)
        return self.games[game_id].get_turn_nowait()

    async def get_next_turn(self, game_id):
        return await self.games[game_id].get_turn()

    def list_games(self) -> GameSession:
        return self.games

    def new_game(self) -> int:
        id = len(self.games)
        self.games.append(GameSession(id))
        return id

    async def join_game(self, game_id:int, player_id:int):
        return await self.games[game_id].join_session(player_id)

    async def join_any_game(self, player_id:int):
        games = list(filter(lambda g: len(g._players) < 2, self.games))
        if len(games) > 0:
            return await self.join_game(games[0].game_id, player_id)
        else:
            game_id = self.new_game()
            return await self.join_game(game_id, player_id)
