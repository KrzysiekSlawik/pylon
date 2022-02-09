import random
from websocket import WebSocketApp, enableTrace
import json as json
from common.messages import MoveMsg, msg_from_json, YourMoveMsg, GameOverMsg


def on_message(ws: WebSocketApp, message):
    try:
        msg_json = json.loads(message)
        msg_obj = msg_from_json(msg_json)
        if type(msg_obj) is YourMoveMsg:
            if len(msg_obj.legal) == 0:
                print("no moves left")
                return
            move = random.choice(msg_obj.legal)
            move["type"] = MoveMsg.__name__
            print(move, "move")
            ws.send(json.dumps(MoveMsg(move).to_dict()))
        if type(msg_obj) is GameOverMsg:
            print(msg_obj)
            ws.close()
    except json.JSONDecodeError:
        print(message)
        print("not a valid json msg, ignoring")


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")
    ws.close()


def connect(game_id: int, player_id: int):
    return WebSocketApp(
        f"ws://127.0.0.1:8000/game/connect?game_id={game_id}&player_id={player_id}",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )


if __name__ == "__main__":
    enableTrace(True)
    while True:
        print("game id")
        game = int(input())
        print("player id")
        player = int(input())
        ws = connect(game_id=game, player_id=player)
        ws.run_forever()
