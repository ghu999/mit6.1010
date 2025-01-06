"""
6.1010 Lab:
Snekoban Game
"""

# import json # optional import for loading test_levels
# import typing # optional import
# import pprint # optional import

# NO ADDITIONAL IMPORTS!


DIRECTION_VECTOR = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}

def make_new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    rows = len(level_description)
    columns = len(level_description[0])
    tset = set()
    cset = set()
    wset = set()
    player = (-1, -1)
    for row in range(rows):
        for col in range(columns):
            tup = (row, col)
            if 'target' in level_description[row][col]:
                tset.add(tup)
            if 'computer' in level_description[row][col]:
                cset.add(tup)
            if 'player' in level_description[row][col]:
                player = (row, col)
            if 'wall' in level_description[row][col]:
                wset.add(tup)
    tfs = frozenset(tset)
    cfs = frozenset(cset)
    wfs = frozenset(wset)
    game_board = (tfs, cfs, player, wfs)
    print(game_board)
    return game_board

def victory_check(game):
    """
     Given a game representation (of the form returned from make_new_game),
     return a Boolean: True if the given game satisfies the victory condition,
     and False otherwise.
     """
    if len(game[0]) == 0: return False
    for target in game[0]:
        if target not in game[1]:
            return False
    for computer in game[1]:
        if computer not in game[0]:
            return False
    return True

def step_game(game, direction):
    """
     Given a game representation (of the form returned from make_new_game),
     return a game representation (of that same form), representing the
     updated game after running one step of the game.  The user's input is given
     by direction, which is one of the following:
         {'up', 'down', 'left', 'right'}.

     This function should not mutate its input.
     """
    targets, computers, player, walls = game
    movement = DIRECTION_VECTOR[direction]
    pos = add_pos(player, movement)

    #if in walls
    if pos in walls:
        return game
    #if there is a computer:
    if pos in computers:
        second_pos = add_pos(pos, movement)
        #next spot is a computer or wall (can't move)
        if second_pos in computers or second_pos in walls:
            return game
        else:
            comp_set = set(computers)
            comp_set.remove(pos)
            comp_set.add(second_pos,)
    else:
        comp_set = computers
    new_game = ((frozenset(targets)), (frozenset(comp_set)), (pos), (frozenset(walls)))
    print(new_game)
    return new_game

def add_pos(pos, direct):
    """
    Adds the coordinates together as tuples
    """
    result = tuple()
    for x in range(len(pos)):
        result = result + (pos[x] + direct[x],)
    return result

def dump_game(game):
    """
    Given a game representation (of the form returned from make_new_game),
    convert it back into a level description that would be a suitable input to
    make_new_game (a list of lists of lists of strings).
    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    dump = []
    height = -1
    width = -1
    for coord in game[3]:
        height = max(height, coord[0])
        width = max(width, coord[1])
    for _ in range(height+1):
        row = []
        for _ in range(width+1):
            row.append([])
        dump.append(row)
    #print(dump)
    names = ["target", 'computer', 'player', 'wall']
    for i in range(4):
        if i == 2:
            dump[game[i][0]][game[i][1]].extend([names[i]])
            continue
        for coord in game[i]:
            dump[coord[0]][coord[1]].extend([names[i]])
    return dump


def solve_puzzle(game):
    """
    Given a game representation (of the form returned from make_new_game), find
    a solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
    visited = set()
    directions = ["left", "right", "up", "down"]
    queue = [([], game)]
    while queue:
        moves, curr_game = queue.pop(0)

        if victory_check(curr_game):
            return moves
        for direction in directions:
            print(direction)
            new_game = step_game(curr_game, direction)
            if new_game not in visited:
                visited.add(new_game)
                queue.append((moves + [direction], new_game))
    return None

if __name__ == "__main__":
    level = [
  [["wall"], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"]],
  [["wall"], [], ["target"], [], [], [], ["wall"]],
  [["wall"], [], ["computer"], [], [], [], ["wall"]],
  [["wall"], [], ["player"], ["computer"], ["target"], [], ["wall"]],
  [["wall"], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"]]
]
    g = make_new_game(level)
    # print("step", step_game(game, 'up'))
    # print(game)
    # dump = dump_game(game)
    # for row in range(len(dump)):
    #     print(dump[row])
    #print(change_game_transform(game))
    print("answer", solve_puzzle(g))
    pass
