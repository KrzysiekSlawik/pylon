from pydantic import BaseModel
from typing import List


Board = List[List[List[int]]]


class Move(BaseModel):
    x: int
    y: int
    level: int


class GameState(BaseModel):
    turn: int
    board: Board
    tokens: List[int]

    def LegalMoves(self):
        current_player = self.turn % 2
        if self.tokens[current_player] <= 0:
            return []


def _supported_empty(board: Board, level):
    if level == 0:
        return [
            {"x": x, "y": y, "level": 0}
            for x in range(0, 4)
            for y in range(0, 4)
            if board[0][x][y] == 0
        ]

    return [
        {"x": x, "y": y, "level": level}
        for x in range(0, 4 - level)
        for y in range(0, 4 - level)
        if board[level][x][y] == 0
        and all(
            [
                board[level - 1][xi][yi]
                for xi in range(x, x + 2)
                for yi in range(y, y + 2)
            ]
        )
    ]


def _legal_cat_put(board):
    s = [m for l in [_supported_empty(board, level) for level in range(0, 4)] for m in l]
    for p in s:
        p["cat"] = "put"
    return s


def _movable(board, level, player):
    return [
        {"x": x, "y": y, "level": level}
        for x in range(0, 4 - level)
        for y in range(0, 4 - level)
        if board[level][x][y] == player
        and not any(
            [
                board[level + 1][xi][yi]
                for xi in range(max(0, x - 1), min(3 - level, x + 1))
                for yi in range(max(0, y - 1), min(3 - level, y + 1))
            ]
        )
    ]


def _legal_cat_move(board, player):
    mv0 = _movable(board, 0, player)
    sp1 = _supported_empty(board, 1)
    res = [
        {
            "cat": "move",
            "x": s["x"],
            "y": s["y"],
            "level": s["level"],
            "take_x": m["x"],
            "take_y": m["y"],
            "take_level": m["level"],
        }
        for s in sp1
        for m in mv0
        if m
        not in [
            {"x": xi, "y": yi, "level": 0}
            for xi in [s["x"], s["x"] + 1]
            for yi in [s["y"], s["y"] + 1]
        ]
    ]
    mv1 = _movable(board, 1, player)
    sp2 = _supported_empty(board, 2)
    res += [
        {
            "cat": "move",
            "x": s["x"],
            "y": s["y"],
            "level": s["level"],
            "take_x": m["x"],
            "take_y": m["y"],
            "take_level": m["level"],
        }
        for s in sp2
        for m in mv1
        if m
        not in [
            {"x": xi, "y": yi, "level": 1}
            for xi in [s["x"], s["x"] + 1]
            for yi in [s["y"], s["y"] + 1]
        ]
    ]
    return res

def _legal_cat_square(board, player)

def generate_empty_board() -> Board:
    return [[[0 for _ in range(0, k)] for _ in range(0, k)] for k in [4, 3, 2, 1]]


def legal_moves(board, turn):
    res = _legal_cat_put(board)
    res += _legal_cat_move(board, turn % 2 + 1)
    return res
