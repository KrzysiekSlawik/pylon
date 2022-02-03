from json import dumps
from typing import List
from common.pylos import Board


class Msg:
    def __init__(self, json_msg) -> None:
        self.type = self.__class__.__name__

    def to_json(self):
        return self.__dict__


class MoveMsgError(Exception):
    pass


class MoveMsg(Msg):
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
            self.take_sq_x: int = json_msg['take_sq_x']
            self.take_sq_y: int = json_msg['take_sq_y']
            self.take_sq_level: int = json_msg['take_sq_level']

        level_max = 4 - self.level
        if not 0 <= self.x < level_max:
            raise MoveMsgError


class GameStateMsg(Msg):
    def __init__(self, json_msg) -> None:
        super().__init__(json_msg)
        self.turn: int = json_msg['turn']
        self.players_ids: List[int] = json_msg['players_ids']
        self.players_names: List[str] = json_msg['players_names']
        self.tokens: List[int] = json_msg['tokens']
        self.board: Board = json_msg['board']
        self.legal = json_msg['legal']


class GameOverMsg(Msg):
    def __init__(self, json_msg) -> None:
        super().__init__(json_msg)
        self.winner_id: int = json_msg['winner_id']
        self.winner_name: str = json_msg['winner_name']
        self.winner_tokens: int = json_msg['winner_tokens']


class BadMsgResp(Msg):
    def __init__(self, json_msg) -> None:
        super().__init__(json_msg)
        self.detail: str = json_msg['detail']


def msg_from_json(json):
    msg_type = json['type']
    if msg_type == MoveMsg.__name__:
        return MoveMsg(json)
    if msg_type == GameStateMsg.__name__:
        return GameStateMsg(json)
    if msg_type == BadMsgResp.__name__:
        return BadMsgResp(json)
    raise TypeError