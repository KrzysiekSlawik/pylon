from json import dumps
from typing import List
from common.pylos import Board


class Msg:
    def __init__(self, json_msg) -> None:
        self.type = self.__class__.__name__

    def to_json(self):
        """
        returns dict
        """
        return self.__dict__


class MoveMsgError(Exception):
    pass


class MoveMsg(Msg):
    """
    Represents move data, send it to make move
    - **cat**: put (put single token), move (move token up), square (finish square and remove 2 tokens from board)
    - **x**: x coordinate of token being put
    - **y**: y coordinate of token being put
    - **level**: level of token being put
    - prefix **take**: coordinates of token being moved (if cat == move) or coordinate of token being removed (if cat == square)
    - predix **take_sq**: coordinates of token being removed, if only one token is being removed *take_sq** coordinates should equal -1
    """
    def __init__(self, json_msg) -> None:
        super().__init__(json_msg)
        self.cat = json_msg['cat']  # 'put', move, square
        self.x: int = json_msg['x']
        self.y: int = json_msg['y']
        self.level: int = json_msg['level']
        if self.cat == 'move' or self.cat == 'square':
            self.take_x: int = json_msg['take_x']
            self.take_y: int = json_msg['take_y']
            self.take_level: int = json_msg['take_level']
        if self.cat == 'square':
            self.take_sq_x: int = json_msg['take_sq_x']  # -1 indicates square move with only one token taken
            self.take_sq_y: int = json_msg['take_sq_y']  # -1 indicates square move with only one token taken
            self.take_sq_level: int = json_msg['take_sq_level']  # -1 indicates square move with only one token taken

        level_max = 4 - self.level
        if not 0 <= self.x < level_max:
            raise MoveMsgError


class GameStateMsg(Msg):
    """
    Represents game state
    - **turn**: current game turn
    - **players_ids**: players ids that are connected to game (at most 2)
    - **players_names**: names of players that are connected to game
    - **tokens**: remaining tokens of players
    - **board**: current state of board (0 => empty, 1 => 1st player, 2 => 2nd player)
    - **legal**: list of all legal moves
    """
    def __init__(self, json_msg) -> None:
        super().__init__(json_msg)
        self.turn: int = json_msg['turn']
        self.players_ids: List[int] = json_msg['players_ids']
        self.players_names: List[str] = json_msg['players_names']
        self.tokens: List[int] = json_msg['tokens']
        self.board: Board = json_msg['board']
        self.legal = json_msg['legal']

class YourMoveMsg(Msg):
    """
    Same as GameStateMsg but it indicates that its your turn
    """
    def __init__(self, json_msg) -> None:
        super().__init__(json_msg)
        self.turn: int = json_msg['turn']
        self.players_ids: List[int] = json_msg['players_ids']
        self.players_names: List[str] = json_msg['players_names']
        self.tokens: List[int] = json_msg['tokens']
        self.board: Board = json_msg['board']
        self.legal = json_msg['legal']


class GameOverMsg(Msg):
    """
    Represents game over summary
    - **winner_id**: id of player that won
    - **winner_name**: name of player that won
    - **winner_tokens**: remaining tokens of player that won
    """
    def __init__(self, json_msg) -> None:
        super().__init__(json_msg)
        self.winner_id: int = json_msg['winner_id']
        self.winner_name: str = json_msg['winner_name']
        self.winner_tokens: int = json_msg['winner_tokens']


class BadMsgResp(Msg):
    """
    Represents responce for invalid message
    - **detail**: detailed information why message is considered invalid
    """
    def __init__(self, json_msg) -> None:
        super().__init__(json_msg)
        self.detail: str = json_msg['detail']


def msg_from_json(json):
    """
    json msg casting to object representing msg of given type
    """
    msg_type = json['type']
    if msg_type == MoveMsg.__name__:
        return MoveMsg(json)
    if msg_type == GameStateMsg.__name__:
        return GameStateMsg(json)
    if msg_type == YourMoveMsg.__name__:
        return YourMoveMsg(json)
    if msg_type == BadMsgResp.__name__:
        return BadMsgResp(json)
    raise TypeError