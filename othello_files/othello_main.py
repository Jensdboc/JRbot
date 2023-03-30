def simulate(white, black, board, coords):

    player = white if board.turn == 'white' else black
    move = player.move(board, coords)
    print(move)

    if isinstance(move, str):
        return move

    if len(move) == 0:
        board.turn = 'black' if board.turn == 'white' else 'white'
        if player == white:
            return "Bot didn't find a place to put his stuff! Your turn now :)"
        else:
            return "Player didn't find a place to put his stuff!"
    else:
        if board.turn == 'white':
            board.board[move[0]][move[1]] = '⬜'
            board.turn_token(move, '⬜', '⬛')
            board.white_played.append(move[0] * 8 + move[1])
            board.turn = 'black'
        else:
            board.board[move[0]][move[1]] = '⬛'
            board.turn_token(move, '⬛', '⬜')
            board.black_played.append(move[0] * 8 + move[1])
            board.turn = 'white'
    return board
