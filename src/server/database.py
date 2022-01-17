from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from common.pylon import GameState

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
        self.games:list[GameState] = []

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

    def new_game(self) -> GameState:
        id = len(self.games)
        self.games.append(GameState(game_id=id,
                                    player_id=[],
                                    endtime=0,
                                    board=[[[0 for i in range(0,k)] for i in range(0,k)]for k in [4,3,2,1]]))
        return id

    def join_game(self, game_id:int, player_id:int) -> bool:
        if len(self.games[game_id].player_id) >= 2:
            return False
        self.games[game_id].player_id.append(player_id)
        return True

    def join_any_game(self, player_id:int) -> bool:
        games = list(filter(lambda g: len(g.player_id) < 2, self.games))
        if len(games) > 0:
            self.join_game(games[0].game_id, player_id)
        else:
            game_id = self.new_game()
            self.join_game(game_id, player_id)
        return True

    def list_games(self):
        return self.games

    def list_players(self):
        return self.session.query(Player).all()