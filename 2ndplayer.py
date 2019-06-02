from random import randint, choice
import math
import socketio
from copy import  deepcopy
import numpy as np

tileRep = ['_', 'X', 'O'],
N = 8

red_flag = 0

sio = socketio.Client()

pointBoard = [24, 3, 3, 3, 3, 3, 3, 24,
              3, -12, -2, -2, -2, -2, -12, 3,
              3, -2, 1, 1, 1, 1, -2, 3,
              3, -2, 1, 1, 1, 1, -2, 3,
              3, -2, 1, 1, 1, 1, -2, 3,
              3, -2, 1, 1, 1, 1, -2, 3,
              3, -12, -2, -2, -2, -2, -12, 3,
              24, 3, 3, 3, 3, 3, 3, 24]


def ix(row,col):
    print(row)
    print(col)
    print('abcdefgh'.index(col))
    return (row-1) * N + 'abcdefgh'.index(col)

def humanBoard(board):
    result = '    A  B  C  D  E  F  G  H'
    for i in range(len(board)):
        print("i:{}".format(i))
        if(i % N == 0):
            result += '\n\n' + str((int(math.floor(i / N)) + 1)) + ' '

        result += ' ' + str(tileRep[board[i % 2]]) + ' '
        print(result)
    return result

def validateHumanPosition(position):
    validated = len(position) == 2
    if(validated):
        row = int(position[0])
        col = position[1].lower()
        return (1 <= row and row <= N) and ('abcdefgh'.index(col) >= 0)
    return False

##def max_value(position):
##    mv = float("-inf")
##    for child in position:
##        value_eval = max_value(child)
##        mv = max(mv,value_eval)
##    return mv
##
##def min_value(position):
##    mv = float("inf")
##    for child in position:
##        value_eval = min_value(child)
##        mv = min(mv,value_eval)
##    return mv
##

def player1_score(board):
    player1total=board.count(1)
    return player1total

def player2_score(board):
    player2total=board.count(2)
    return player2total


def possible_moves(board,player):
    move_list = []
    for i in range(0,64):
        if board[i] == player:
            #moverse a la izquierda
            if i % 8 > 1:
                if board[i-1] != player and board[i-1] != 0:
                    if(board[i-2] == 0):
                        move_list.append(i-2)
            # moverse a la derecha
            if i % 8 < 6:
                if board[i+1] != player and board[i+1] !=0:
                    if(board[i+2] == 0):
                        move_list.append(i+2)
            #moverse hacia arriba
            if i > 15:
                if board[i-8] != player and board[i-8] !=0:
                    if(board[i-16] == 0):
                        move_list.append(i-16)
            #moverse hacia abajo
            if i < 48:
                if board[i+8] != player and board[i+8] !=0:
                    if(board[i+16] == 0):
                        move_list.append(i+16)
    return move_list

def inside_board(position):
    if position < 64 and position >= 0:
        return True
    else:
        return False

#no es completamente correcto pero esta simplificado
def possible_moves_reworked(board,player):
    if player == 1:
        enemy = 2
    elif player ==2:
        enemy = 1
    move_list = []

    for i in range(0,64):
        if board[i]  == enemy:
            # derecha
            if(inside_board(i+1) and board[i+1] == 0):
                move_list.append(i+1)
            # izquierda
            if(inside_board(i-1) and board[i-1] == 0):
                move_list.append(i-1)
            # arriba
            if (inside_board(i - 8) and board[i - 8] == 0):
                move_list.append(i-8)
            # abajo
            if (inside_board(i + 8) and board[i + 8] == 0):
                move_list.append(i + 8)

    return move_list


def enemy_moves(board, player):
    move_list = []

    for i in range(0, 64):
        if board[i] == player:
            # derecha
            if(inside_board(i+1) and board[i+1] == 0):
                move_list.append(i+1)
            # izquierda
            if(inside_board(i-1) and board[i-1] == 0):
                move_list.append(i-1)
            # arriba
            if (inside_board(i - 8) and board[i - 8] == 0):
                move_list.append(i-8)
            # abajo
            if (inside_board(i + 8) and board[i + 8] == 0):
                move_list.append(i + 8)
    return  move_list

def create_all_moves(initial_board, current_player):
    current_player_moves = possible_moves_reworked(initial_board,current_player)
    next_moves = []
    for player_move in current_player_moves:
        next_board = deepcopy(initial_board)
        next_board[player_move] = current_player
        next_moves.append(next_board)
    return next_moves


def create_scores(next_moves,scoreboard):
    possible_scores = []
    print("next moves : {}".format(next_moves))
    for move in next_moves:
        move_prime = np.array(move)
        scoreboard = np.array(scoreboard)
        calculate_score = (move_prime * scoreboard)
        calculate_score = calculate_score.sum()
        possible_scores.append(calculate_score)
    return  possible_scores






def minimax(depth, nodeIndex, player, board, alpha, beta):
    if depth == 1:
        return board[nodeIndex]

    if player == 1:
        best = float("-inf")
        for i in range(0,2):
            val = minimax(depth + 1, nodeIndex * 2 + i, 2, board, alpha, beta)
            best = max(best,val)
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best

    else:
        best = float("inf")
        for i in range(0,2):
            val = minimax(depth + 1, nodeIndex * 2 + i, 1, board, alpha, beta)
            best = min(best, val)
            beta = min(beta,best)
            if beta <= alpha:
                break
        return best

@sio.on('connect')
def on_connect():
    print("Conectado: {}".format(userName))
    sio.emit('signin',{ 'user_name': userName, 'tournament_id': tournamentID, 'user_role': 'player' })

@sio.on('ready')
def on_ready(data):
    global red_flag
    row_generator = []
    full_board = []
    print("About to move. Board:\n")
    print('player_turn: {}'.format(data['player_turn_id']))
    print(data['board'])
    print("score: {}".format(player1_score(data['board'])))
    #for i in range(len(data['board'])):
     #   if(i % 8 == 0 and i!=0 ):
      #      print("\n")
        #print(data['board'],end="")
    #print("\n")
        
    #movement = ""
    list_of_cols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    list_of_cols1 = ['C', 'D', 'E','F']
    
    #movement = randint(0,63)

    #calcular todas las jugadas
    all_moves = create_all_moves(data['board'],data['player_turn_id'])

        
    scores = create_scores(all_moves, pointBoard)

    print("scores: {}".format(scores))

    if(len(scores) > 1):
        alpha_beta = minimax(0, 0, data['player_turn_id'], scores, float("-inf"), float("inf"))
        wheretomove = scores.index(alpha_beta)
    else:
        #solo 1 jugada
        wheretomove = 0
    #if red_flag == wheretomove:
        #print("hello there general kenobi")
        #dont pick this
       # scores[wheretomove] = float("inf")
      #  alpha_beta = minimax(0, 0, data['player_turn_id'], scores, float("-inf"), float("inf"))  
     #   wheretomove = scores.index(alpha_beta)

    #print("red_flag: {0}, wheretomove: {1}".format(red_flag,wheretomove))
    #red_flag = wheretomove
    
        #wheretomove = scores.index(scores.choice())
        

    playerwillmove = possible_moves_reworked(data['board'],data['player_turn_id'])

    if(playerwillmove):
        print("wheretomove: {}".format(wheretomove))
        movement  = playerwillmove[wheretomove]
    else:
        movement = randint(0,64)
    
    if red_flag == wheretomove:
        print("hello there general kenobi")
        if(playerwillmove):
            movement = choice(playerwillmove)
        else:
            movement = randint(0,64)
        

    print("red_flag: {0}, wheretomove: {1}".format(red_flag,wheretomove))
    red_flag = wheretomove
    

    #pop si no es una movida que se pueda realizar
    #scores.pop(wheretomove)

    print("movement: {}".format(movement))
    #while(not(validateHumanPosition(movement))):
     #   movement = str(randint(3,6)) + choice(list_of_cols1)
        

    sio.emit('play', {'player_turn_id': data['player_turn_id'], 'tournament_id': tournamentID, 'game_id': data['game_id'], 'movement': movement} )

@sio.on('finish')
def on_finish(data):
    print("Game {} has finished".format(data['game_id']))
    print("ready to play again")

    sio.emit('player_ready', {'tournament_id': tournamentID, 'game_id': data['game_id'], 'player_turn_id': data['player_turn_id'] })


#sio.connect('http://192.168.88.253:4000')
#sio.connect('http://192.168.1.127:4000')
sio.connect('http://localhost:4000')
userName = 'Kappa' 
tournamentID = 142857

