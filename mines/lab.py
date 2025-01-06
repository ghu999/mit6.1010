"""
6.101 Lab:
Mines
"""
#!/usr/bin/env python3

# import typing  # optional import
# import pprint  # optional import
import doctest

# NO ADDITIONAL IMPORTS ALLOWED!


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    keys = ("board", "dimensions", "state", "visible")
    # ^ Uses only default game keys. If you modify this you will need
    # to update the docstrings in other functions!
    for key in keys:
        val = game[key]
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f"{key}:")
            for inner in val:
                print(f"    {inner}")
        else:
            print(f"{key}:", val)


# 2-D IMPLEMENTATION
def new_game_2d(nrows, ncolumns, mines):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Parameters:
       nrows (int): Number of rows
       ncolumns (int): Number of columns
       mines (list): List of mines, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: ongoing
    visible:
        [False, False, False, False]
        [False, False, False, False]
    """
    return new_game_nd((nrows, ncolumns), mines)

def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['visible'] to reveal (row, col).  Then, if (row, col) has no
    adjacent mines (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one mine
    is visible on the board after digging (i.e. game['visible'][mine_location]
    == True), 'victory' when all safe squares (squares that do not contain a
    mine) and no mines are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing', 'hidden': 4}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: victory
    visible:
        [False, True, True, True]
        [False, False, True, True]

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing', 'hidden': 7}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    state: defeat
    visible:
        [True, True, False, False]
        [False, False, False, False]
    """
    return dig_nd(game, (row, col))

def render_2d_locations(game, all_visible=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (mines), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    mines).  game['visible'] indicates which squares should be visible.  If
    all_visible is True (the default is False), game['visible'] is ignored
    and all cells are shown.

    Parameters:
       game (dict): Game state
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                    by game['visible']

    Returns:
       A 2D array (list of lists)

    >>> game = {'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, True, False],
    ...                   [False, False, True, False]]}
    >>> render_2d_locations(game, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations(game, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    return render_nd(game, all_visible)

def render_2d_board(game, all_visible=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                           by game['visible']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'visible':  [[True, True, True, False],
    ...                            [False, False, True, False]]})
    '.31_\\n__1_'
    """
    locs = render_2d_locations(game, all_visible)
    result = ""
    for row in locs:
        for char in row:
            result += char
        result+="\n"
    return result[0:len(result)-1]

# N-D IMPLEMENTATION

def create_nd_array(dimensions, value):
    """
    Given a dimensions tuple (x, y, z, a, etc.)
    return an n-dimensional array filled with the given value.
    """
    result = []
    if len(dimensions) == 1:
        for _ in range(dimensions[0]):
            result.append(value)
        return result
    rest = dimensions[1:]
    for _ in range(dimensions[0]):
        result.append(create_nd_array(rest, value))
    return result

def find_value(board, coords):
    """
    Given an n-d array and coords, find the value of at the given coords.
    """
    if len(coords) == 1:
        return board[coords[0]]
    return find_value(board[coords[0]], coords[1:])

def set_value(board, coords, val):
    """
    Given an n-d array, coords, and value, set the value of at the given coords.
    """
    if len(coords) == 1:
        board[coords[0]] = val
        return
    set_value(board[coords[0]], coords[1:], val)

def all_neighbors(dimensions, coords):
    """
    Find all the neighbors of a coordinate
    """
    neighbors = []
    def recur(index, curr_neighbor):
        if len(curr_neighbor) == index:
            neighbors.append(tuple(curr_neighbor))
            return
        for dx in [-1, 0, 1]:
            new_val = coords[index] + dx
            if 0 <= new_val < dimensions[index]:
                curr_neighbor[index] = new_val
                recur(index + 1, curr_neighbor.copy())
                curr_neighbor[index] = coords[index]
    recur(0, list(coords).copy())
    #print(neighbors)
    neighbors.remove(coords)
    return neighbors

def all_possible_coords(dimensions):
    """
    Returns a list of all possible cordinates given a dimensions tuple
    """
    if len(dimensions) == 1:
        for i in range(dimensions[0]):
            yield (i,)
    else:
        yield from { (i,) + neighbor
        for i in range(dimensions[0])
        for neighbor in all_possible_coords(dimensions[1:])}

def new_game_nd(dimensions, mines):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Args:
       dimensions (tuple): Dimensions of the board
       mines (list): mine locations as a list of tuples, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    game = {}
    game['dimensions'] = dimensions
    game['state'] = 'ongoing'
    size = 1
    for dimension in dimensions:
        size *= dimension
    game['hidden'] = size
    game['hidden'] -= len(mines)
    board = create_nd_array(dimensions, 0)
    for mine in mines:
        set_value(board, mine, '.')
    for mine in mines:
        neighbors = all_neighbors(dimensions, mine)
        for neighbor in neighbors:
            val = find_value(board, neighbor)
            if val != '.':
                set_value(board, neighbor, int(val) + 1)
    visible = create_nd_array(dimensions, False)
    game['board'] = board
    game['visible'] = visible
    return game


def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the visible to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    mine.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one mine is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a mine) and no mines are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing', 'hidden': 13}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing', 'hidden': 13}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: defeat
    visible:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    if game["state"] != "ongoing": # victory or defeat
        return 0
    shown = reveal(game, coordinates)
    if find_value(game["board"], coordinates) != '.':
        game['hidden'] -= shown
    if game["hidden"] == 0:
        game["state"] = "victory"
    return shown

def reveal(game, coord):
    """
    Count how many squares are revealed after one dig
    """
    visible =  find_value(game["visible"], coord)
    val = find_value(game["board"], coord)
    if visible:
        return 0
    set_value(game["visible"], coord, True)
    if val == '.':
        game['state'] = 'defeat'
        return 1
    if val == 0:
        neighbors = all_neighbors(game["dimensions"], coord)
        revealed = 1
        for neighbor in neighbors:
            revealed += reveal(game, neighbor)
        return revealed
    return 1

def render_nd(game, all_visible=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (mines), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    mines).  The game['visible'] array indicates which squares should be
    visible.  If all_visible is True (the default is False), the game['visible']
    array is ignored and all cells are shown.

    Args:
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                           by game['visible']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [True, True],
    ...                [True, True]],
    ...               [[False, False], [False, False], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    coords = all_possible_coords(game["dimensions"])
    if all_visible:
        result = create_nd_array(game["dimensions"], ' ')
        for coord in coords:
            val = find_value(game["board"], coord)
            if val != 0:
                set_value(result, coord, str(val))
        return result
    else:
        result = create_nd_array(game["dimensions"], '_')
        for coord in coords:
            val = find_value(game["board"], coord)
            visible = find_value(game["visible"], coord)
            if visible:
                if val != 0:
                    set_value(result, coord, str(val))
                else:
                    set_value(result, coord, ' ')
        return result

if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    #
    # doctest.run_docstring_examples(
    #    dig_nd,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )
   #board = create_nd_array((3, 3, 3), 0)
    #set_value(board, (2, 1, 1), 3)
    # print(board)
    # print(find_value(board, (2, 1, 1)))
    #print(all_neighbors((10, 10, 10), (2, 3, 5)))
    #print(all_possible_coords((2, 2, 2)))
