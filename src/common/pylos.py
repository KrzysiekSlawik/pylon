from typing import List
from copy import deepcopy


Board = List[List[List[int]]]


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


def _takeable(board, level, player):
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
    mv0 = _takeable(board, 0, player)
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
    mv1 = _takeable(board, 1, player)
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

def is_on_board(board, level, x, y) -> bool:
    """
    checks if coordinates are in board bounds
    """
    try:
        board[level][x][y]
        return True
    except IndexError:
        return False

def _legal_cat_square(board, player):
    legal_put = [m for l in [_supported_empty(board, level) for level in range(0, 3)] for m in l]
    legal_square = [m for m in legal_put
                    if any(
                        [
                            3 == len([1 for (xi,yi) in [
                                    (m['x'], m['y'] - 1),
                                    (m['x'] + 1, m['y'] - 1),
                                    (m['x'] + 1, m['y'])
                                 ]
                                 if is_on_board(board, m['level'], xi, yi) and board[m['level']][xi][yi] == player]),
                            3 == len([1 for (xi,yi) in [
                                    (m['x'] + 1, m['y']),
                                    (m['x'] + 1, m['y'] + 1),
                                    (m['x'], m['y'] + 1)
                                 ]
                                 if is_on_board(board, m['level'], xi, yi) and board[m['level']][xi][yi] == player]),
                            3 == len([1 for (xi,yi) in [
                                    (m['x'], m['y'] + 1),
                                    (m['x'] - 1, m['y'] + 1),
                                    (m['x'] - 1, m['y'])
                                 ]
                                 if is_on_board(board, m['level'], xi, yi) and board[m['level']][xi][yi] == player]),
                            3 == len([1 for (xi,yi) in [
                                    (m['x'] - 1, m['y']),
                                    (m['x'] - 1, m['y'] - 1),
                                    (m['x'], m['y'] - 1)
                                 ]
                                 if is_on_board(board, m['level'], xi, yi) and board[m['level']][xi][yi] == player]),
                        ]
                    )]
    res = []
    for sq in legal_square:
        bcp1 = deepcopy(board)
        bcp1[sq['level']][sq['x']][sq['y']] = player
        takeable1 = [m for l in [_takeable(bcp1, level, player) for level in range(0, 3)] for m in l]
        res += [
            {
                "cat": "square",
                "level": sq["level"],
                "x": sq["x"],
                "y": sq["y"],
                "take_level": t["level"],
                "take_x": t["x"],
                "take_y": t["y"],
                "take_sq_level": -1,
                "take_sq_x": -1,
                "take_sq_y": -1,
            }
            for t in takeable1
        ]
        for t in takeable1:
            bcp2 = deepcopy(bcp1)
            bcp2[t['level']][t['x']][t['y']] = 0
            takeable2 = [m for l in [_takeable(bcp2, level, player) for level in range(0, 3)] for m in l]
            res += [
                {
                    "cat": "square",
                    "level": sq["level"],
                    "x": sq["x"],
                    "y": sq["y"],
                    "take_level": t["level"],
                    "take_x": t["x"],
                    "take_y": t["y"],
                    "take_sq_level": t2["level"],
                    "take_sq_x": t2["x"],
                    "take_sq_y": t2["y"],
                }
                for t2 in takeable2
            ]
    return res




def generate_empty_board() -> Board:
    """
    returns empty board - starting state of board
    """
    return [[[0 for _ in range(0, k)] for _ in range(0, k)] for k in [4, 3, 2, 1]]


def legal_moves(board, turn) -> List[dict]:
    """
    returns legal moves of player that should move
    - **board**: board state
    - **turn**: game turn, used to determine whos turn it is
    """
    res = _legal_cat_put(board)
    res += _legal_cat_move(board, turn % 2 + 1)
    res += _legal_cat_square(board, turn % 2 + 1)
    return res
