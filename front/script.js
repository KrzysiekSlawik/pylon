websocket = new WebSocket(
  "ws://127.0.0.1:8000/game/connect?game_id=0&player_id=0"
);

websocket.onmessage = (event) => {
    let data = JSON.parse(event.data)
    console.log(data)
    for (level = 0; level < 4; level++) {
        for (x = 0; x < 4 - level; x++) {
            for (y = 0; y < 4 - level; y++) {
                let id = `${level}_${x}_${y}`;
                let sphere = document.getElementById(id);
                let value = data.board[level][x][y];
                switch (value)
                {
                    case 0:
                        sphere.className = "circle empty";
                        break;
                    case 1:
                        sphere.className = "circle light";
                        break;
                    case 2:
                        sphere.className = "circle dark";
                        break;
                    default:
                        alert("bad value");
                }
            }
        }
    }
    document.getElementById("player1Name").innerHTML = `Light: ${data.players_names[0]}`
    document.getElementById("tokenPlayer1").innerHTML = `Tokens: ${data.tokens[0]}`

    document.getElementById("player2Name").innerHTML = `Dark: ${data.players_names[1]}`
    document.getElementById("tokenPlayer2").innerHTML = `Tokens: ${data.tokens[1]}`
};