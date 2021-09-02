#!/usr/bin/env python3
import os


def TR(x): return '\x1b[38;2;255;0;0m' + str(x) + \
    '\x1b[m' if not x else '\x1b[38;2;0;255;0m' + str(x) + '\x1b[m'


t_col = {False: '\x1b[1;38;2;0;0;0m',
         True: '\x1b[1;38;2;255;255;255m', None: '\x1b[2m'}

# All pieces attributes and mooving algorithms
pieces = {  # n: name, p:, print, t: team, vp: valid pos, vt: valid type, vm: valid move, pieces: ♔ ♕ ♖ ♗ ♘ ♙ ♚ ♛ ♜ ♝ ♞ ♟
    'k': {'n': 'king', 'p': '♔', 't': None,
            'vp': lambda a, b, t: True if b[0] - a[0] in [-1, 0, 1] and b[1] - a[1] in [-1, 0, 1] else False,

            'vm': lambda a, b, p1, p2, br: True if b[0] - a[0] in [-1, 0, 1] and b[1] - a[1] in [-1, 0, 1] else False,

          'vt': lambda a, b, x, y: True if not a['t'] == b['t'] else False},
    'q': {'n': 'queen', 'p': '♕', 't': None,
          'vp': lambda a, b, t: True if (b[0] - a[0] == b[1] - a[1] or not (b[0] - a[0]) + (b[1] - a[1])) or
          (not b[0] - a[0] and b[1] - a[1]) or (b[0] - a[0] and not b[1] - a[1]) else False,

          'vm': lambda a, b, p1, p2, br: False if
          ((b[0] - a[0] == b[1] - a[1] and dia_coll(a[0], a[1], b[0], b[1], br))) or
          ((not (b[0] - a[0]) + (b[1] - a[1]) and dia_coll(a[0], a[1], b[0], b[1], br))) or
          ((not b[0] - a[0] and b[1] - a[1] and st_coll(a[0], b[0], a[1], b[1], br, False))) or
          ((b[0] - a[0] and not b[1] - a[1]
            and st_coll(a[1], b[1], a[0], b[0], br, True)))
          else True,

          'vt': lambda a, b, x, y: True if not a['t'] == b['t'] else False},
    'r': {'n': 'rook', 'p': '♖', 't': None,
          'vp': lambda a, b, t: True if (not b[0] - a[0] and b[1] - a[1]) or (b[0] - a[0] and not b[1] - a[1]) else False,

          'vm': lambda a, b, p1, p2, br: False if
          (b[1] - a[1] and st_coll(a[0], b[0], a[1], b[1], br, False)) or
          (b[0] - a[0] and st_coll(a[1], b[1], a[0], b[0], br, True)) else True,

          'vt': lambda a, b, x, y: True if not a['t'] == b['t'] else False},
    'c': {'n': 'knight', 'p': '♘', 't': None,
          'vp': lambda a, b, t: True if (b[0] - a[0] in [-2, 2] and b[1] - a[1] in [-1, 1]) or (b[0] - a[0] in [-1, 1] and b[1] - a[1] in [-2, 2]) else False,

          'vm': lambda a, b, p1, p2, br: True,

          'vt': lambda a, b, x, y: True if not a['t'] == b['t'] else False},
    'b': {'n': 'bishop', 'p': '♗', 't': None,
          'vp': lambda a, b, t: True if b[0] - a[0] and b[1] - a[1] and (b[0] - a[0] == b[1] - a[1] or not (b[0] - a[0]) + (b[1] - a[1])) else False,

          'vm': lambda a, b, p1, p2, br: False if
          (b[0] - a[0] == b[1] - a[1] and dia_coll(a[0], a[1], b[0], b[1], br)) or
          (not (b[0] - a[0]) + (b[1] - a[1])
           and dia_coll(a[0], a[1], b[0], b[1], br))
          else True,

          'vt': lambda a, b, x, y: True if not a['t'] == b['t'] else False},
    'p': {'n': 'pawn', 'p': '♙', 't': None,
          'vp': lambda a, b, t: True if
          (((b[0] - a[0] == -1 and b[1] - a[1] in [-1, 0, 1]) or (b[0] - a[0] == -2 and a[0] == 6)) and t) or
          (((b[0] - a[0] == 1 and b[1] - a[1] in [-1, 0, 1]) or (b[0] - a[0] == 2 and a[0] == 1)) and not t) else False,

          'vm': lambda a, b, p1, p2, br: False if
          (b[0] - a[0] == -2 and not br[b[0] + 1][b[1]]['t'] == None) or
          (b[0] - a[0] == 2 and not br[b[0] - 1][b[1]]['t'] == None) or
          (b[1] - a[1] in [-1, 1] and not (p1['t'] == (not p2['t']))) else True,

          'vt': lambda a, b, x, y: True if (b['t'] == None and y[1] - x[1] == 0) or
          (((a['t'] and b['t'] == False) or (b['t'] and a['t'] == False)) and y[1] - x[1] in [-1, 1]) else False},
    'n': {'n': 'nonce', 'p': 'n',  't': None,
          'vp': lambda a, b, t: False,

          'vm': lambda a, b, p1, p2, br: False,

          'vt': lambda a, b, x, y: True if not a['t'] == b['t'] else False},
}

# vm algorithms
# Straght movement


def st_coll(a0, b0, a1, b1, br, v): return len(list(filter(lambda x: not x,
                                                           [False if (v and not br[i][a0]['t'] == None) or (not v and not br[a0][i]['t'] == None) else True for i in range(
                                                            a1 + int((b1 - a1) / abs(b1 - a1)), b1, int((b1 - a1) / abs(b1 - a1)))]
                                                           ))) > 0

# Diagonal movement


def dia_tup(a0, a1, b0, b1): return list(zip(
    range(
        a0 + int((b0 - a0) / (abs(b0 - a0) if not b0 - a0 == 0 else 1)),
        b0,
        int((b0 - a0) / (abs(b0 - a0) if not b0 - a0 == 0 else 1))),
    range(
        a1 + int((b1 - a1) / (abs(b1 - a1) if not b1 - a1 == 0 else 1)),
        b1,
        int((b1 - a1) / (abs(b1 - a1) if not b1 - a1 == 0 else 1)))
))


def dia_coll(a0, a1, b0, b1, br): return len(list(filter(lambda x: not x,
                                                         # (print( a0, a1, b0, b1) or print(dia_tup(a0, a1, b0, b1)) or True) and
                                                         [False if not br[i[0]][i[1]]['t'] == None else True for i in dia_tup(a0, a1, b0, b1)]))) > 0


board_list = [   # Lower is black, upper is white. n is empty
    'rcbqkbcr',
    'pppppppp',
    'nnnnnnnn',
    'nnnnnnnn',
    'nnnnnnnn',
    'nnnnnnnn',
    'PPPPPPPP',
    'RCBQKBCR'
]

board_list_o = [   # Lower is black, upper is white. n is empty
    'nnnknnnnp',
    'qqqqqqqqp',
    'nnnnnnnnp',
    'nnnnnnnnp',
    'QQQQQQQQp',
    'npnKnnnnp',
    'nnnnnnpnp',
    'nnnnnbnnn',
    'ppppppppP'
]

# Constant of board size
size = 8
size_o = 9

# Simple dictionary deep copy


def memcpy(x): return {key: val for key, val in x.items()}

# For printing the board


def pi(i): return print('\x1b[1;38;2;175;105;44m' + str(
    ([' '] + [i for i in range(size, 0, -1)] + [' '])[i + 1]) + '\x1b[m', end=' ')
def pj(j): return print('\x1b[1;38;2;175;105;44m' + (' ' +
                                                     'abcdefghijklmnopqrstuvwxyz'[:size] + ' ')[j+1] + '\x1b[m', end=' ')


def cij(i, j): return pi(i) if j in [-1, size] else pj(j)


def prb(x): return [[print(t_col[board[i][j]['t']] + board[i][j]['p'] + '\x1b[m', end=' ')
                     if j in range(size) and i in range(size) else cij(i, j) for j in range(-1, size + 1)] for i in range(-1, size + 1) if not print()]

# For converting input to correct index


def chtonum(x): return {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 9, 'k': 10, 'l': 11, 'm': 12,
                        'n': 13, 'o': 14, 'p': 15, 'q': 16, 'r': 17, 's': 18, 't': 19, 'u': 20, 'v': 21, 'w': 22, 'x': 23, 'y': 24, 'z': 25}[x]


def invnum(x): return [i for i in range(size, -1, -1)][x]


def convmove(x): return [[invnum(int(x[1])), int(chtonum(x[0]))], [
    invnum(int(x[4])), int(chtonum(x[3]))]]


# Creatin of the board
def create_board():
    board = [[(memcpy(pieces[j]), False) if not j.istitle() else (
        memcpy(pieces[j.lower()]), True) for j in i] for i in board_list]
    for i, v in enumerate(board):
        for j, w in enumerate(v):
            if board[i][j][0]['n'] == 'nonce':
                board[i][j][0]['t'] = None
            elif w[1]:
                board[i][j][0]['t'] = True
            else:
                board[i][j][0]['t'] = False
            board[i][j] = board[i][j][0]
    return board

# Input checker


def action():
    os.system('clear')
    prb(board)
    print('\n\nAction: ', end='')

    def inp_val(x):
        try:
            return True if len(x) in [5, 6, 7] and x[0] in 'abcdefghijklmnopqrstuvwxyz' and int(x[1]) in range(1, size + 1) and x[2] == ' ' and x[3] in 'abcdefghijklmnopqrstuvwxyz' and int(x[4]) in range(1, size + 1) and not x[:2] == x[3:5] else False
        except:
            return False
    while True:
        ch = input()
        if inp_val(ch):
            return ch
        # os.system('clear')
        # prb(board)
        print(
            '\n\x1b[38;2;255;0;0mInvalid input!\x1b[0;2m\t(press enter)\x1b[m', end='')
        input()
        os.system('clear')
        prb(board)
        print('\n\nAction: ', end='')


def move_valid(ch, turn):
    # print(ch)
    p1, p2 = board[ch[0][0]][ch[0][1]], board[ch[1][0]][ch[1][1]]
    pos1, pos2 = [ch[0][0], ch[0][1]], [ch[1][0], ch[1][1]]
    if not p1['t'] == turn:
        print(
            '\n\x1b[38;2;255;0;0mNot your turn!\x1b[0;2m\t(press enter)\x1b[m', end='')
        return False
    if p1['n'] == 'nonce':
        print(
            '\n\x1b[38;2;255;0;0mNonce cannot be moved!\x1b[0;2m\t(press enter)\x1b[m', end='')
        return False
    if not p1['vp'](pos1, pos2, p1['t']):
        print(
            '\n\x1b[38;2;255;0;0mInvalid position!\x1b[0;2m\t(press enter)\x1b[m', end='')
        return False
    if not p1['vm'](pos1, pos2, p1, p2, board):
        print(
            '\n\x1b[38;2;255;0;0mCollision on move!\x1b[0;2m\t(press enter)\x1b[m', end='')
        return False
    if not p1['vt'](p1, p2, pos1, pos2):
        print(
            '\n\x1b[38;2;255;0;0mCannot move on this piece type!\x1b[0;2m\t(press enter)\x1b[m', end='')
        return False

    return True

# Moving


def move(ch):
    res = True if board[ch[1][0]][ch[1][1]]['n'] == 'king' else False
    board[ch[1][0]][ch[1][1]] = board[ch[0][0]][ch[0][1]]
    board[ch[0][0]][ch[0][1]] = memcpy(pieces['n'])
    # prb(board)    # TEMP
    return res


# 16 pieces: one king, one queen, two rooks, two knights, two bishops, and eight pawns
if __name__ == '__main__':
    board = create_board()
    turn = True

    # Main loop
    while True:
        while True:
            ch = action()
            ch = convmove(ch)
            if move_valid(ch, turn):
                break
            input()
        win = move(ch)
        if win:
            os.system('clear')
            prb(board)
            print('\n\n\x1b[1mWhite/Player1 won!\x1b[m') if turn else print(
                '\n\n\x1b[1;38;2;0;0;0mBlack/Player2 won!\x1b[m')
            exit()
        turn = not turn
        # print('\n\n\x1b[0;2mPress enter\x1b[m', end = '') # TEMP
        # input()   # TEMP
