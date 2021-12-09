import math

def in_board_convert(board):
    return 

def out_move_convert(engine_move):
    return

def sigmoid(x):
    #print(x)
    x /= 100.0
    #return x
    global_max = 0.99999999
    global_min = 0.00000001
    if x > 500:
        return global_max
    elif x < -500:
        return global_min
    val = 1.0 / (1.0 + math.pow(10.0, x / -4.0))
    if val == 0:
        return global_min
    if val == 1:
        return global_max
    return val

def quicksort(moves, i, j):
    if i > len(moves) - 1:
        return
    if j < 0:
        return
    if j <= i:
        return

    pivot = i
    n = 0
    while pivot + 1 + n <= j:
        if moves[pivot + 1 + n][0] > moves[pivot][0]:
            temp = [moves[pivot + 1][0], moves[pivot + 1][1]]
            moves[pivot + 1][0] = moves[pivot + 1 + n][0]
            moves[pivot + 1][1] = moves[pivot + 1 + n][1]
            moves[pivot + 1 + n][0] = temp[0]
            moves[pivot + 1 + n][1] = temp[1]

            temp = [moves[pivot][0], moves[pivot][1]]
            moves[pivot][0] = moves[pivot + 1][0]
            moves[pivot][1] = moves[pivot + 1][1]
            moves[pivot + 1][0] = temp[0]
            moves[pivot + 1][1] = temp[1]

            pivot += 1
        else:
            n += 1
    quicksort(moves, pivot + 1, j)
    quicksort(moves, i, pivot - 1)