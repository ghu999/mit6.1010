"""
6.101 Lab 7:
Six Double-Oh Mines
"""

#!/usr/bin/env python3
import os
import lab
import sys
import pickle
import doctest

import pytest

sys.setrecursionlimit(20000)

TEST_DIRECTORY = os.path.dirname(__file__)

TESTDOC_FLAGS = doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE
TESTDOC_SKIP = ['lab']


def test_all_doc_strings_exist():
    """ Checking if docstrings have been written for everything in lab.py """
    tests = doctest.DocTestFinder(exclude_empty=False).find(lab)
    for test in tests:
        if test.name in TESTDOC_SKIP:
            continue
        assert test.docstring, f"Oh no, '{test.name}' has no docstring!"


def test_newsmallgame():
    result = lab.new_game_2d(10, 8, [(7, 3), (2, 6), (8, 7), (4, 4), (3, 5),
                                     (4, 6), (6, 2), (9, 4), (4, 2), (4, 0),
                                     (8, 6), (9, 7), (8, 5), (5, 0), (7, 2),
                                     (5, 3)])
    expected = {"board": [[0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 1, 1, 1],
                          [0, 0, 0, 0, 1, 2, ".", 1],
                          [1, 2, 1, 2, 2, ".", 3, 2],
                          [".", 3, ".", 3, ".", 3, ".", 1],
                          [".", 4, 3, ".", 2, 2, 1, 1],
                          [1, 3, ".", 4, 2, 0, 0, 0],
                          [0, 2, ".", ".", 2, 2, 3, 2],
                          [0, 1, 2, 3, 3, ".", ".", "."],
                          [0, 0, 0, 1, ".", 3, 4, "."]],
                "dimensions": (10, 8),
                "visible": [[False, False, False, False, False, False, False, False],
                         [False, False, False, False, False, False, False, False],
                         [False, False, False, False, False, False, False, False],
                         [False, False, False, False, False, False, False, False],
                         [False, False, False, False, False, False, False, False],
                         [False, False, False, False, False, False, False, False],
                         [False, False, False, False, False, False, False, False],
                         [False, False, False, False, False, False, False, False],
                         [False, False, False, False, False, False, False, False],
                         [False, False, False, False, False, False, False, False]],
                "state": "ongoing"}
    for name in expected:
        assert result[name] == expected[name]


def test_newmediumgame():
    result = lab.new_game_2d(30, 16, [(16, 6), (17, 7), (14, 4), (13, 4),
                                      (0, 7), (21, 6), (2, 5), (5, 5), (6, 10),
                                      (12, 6), (24, 14), (14, 1), (24, 1),
                                      (26, 12), (8, 15), (9, 3), (16, 0),
                                      (19, 13), (15, 14), (13, 10), (18, 10),
                                      (21, 15), (28, 15), (29, 14), (11, 15),
                                      (14, 8), (17, 8), (24, 8), (25, 5),
                                      (2, 1), (10, 3), (27, 2), (17, 6),
                                      (7, 15), (15, 0), (21, 8), (20, 0),
                                      (1, 10), (10, 4), (14, 6), (1, 0),
                                      (4, 11), (27, 0), (9, 13), (23, 5),
                                      (14, 12), (20, 15), (3, 15), (26, 14),
                                      (4, 8), (10, 15), (7, 11), (18, 1),
                                      (25, 4), (26, 3), (22, 14), (28, 2),
                                      (13, 2), (19, 6), (1, 4), (21, 4),
                                      (1, 9), (8, 7), (23, 1), (22, 11),
                                      (19, 5), (18, 7), (0, 6), (26, 4),
                                      (3, 4), (5, 9), (24, 13), (20, 8),
                                      (19, 0), (0, 3), (21, 13), (3, 3),
                                      (28, 9), (11, 1), (12, 10), (24, 10),
                                      (18, 13), (0, 0), (21, 0), (3, 13),
                                      (27, 13), (5, 15), (26, 9), (17, 4),
                                      (7, 9), (19, 9), (24, 7), (22, 5),
                                      (3, 8), (27, 8), (9, 5), (23, 13),
                                      (5, 2), (10, 2)])
    exp_fname = os.path.join(TEST_DIRECTORY, 'test_outputs', 'test2d_newmediumgame.pickle')
    with open(exp_fname, 'rb') as f:
        expected = pickle.load(f)
    for name in expected:
        assert result[name] == expected[name]


def test_newlargegame():
    exp_fname = os.path.join(TEST_DIRECTORY, 'test_outputs', 'test2d_newlargegame.pickle')
    inp_fname = os.path.join(TEST_DIRECTORY, 'test_inputs', 'test2d_newlargegame.pickle')
    with open(exp_fname, 'rb') as f:
        expected = pickle.load(f)
    with open(inp_fname, 'rb') as f:
        inputs = pickle.load(f)
    result = lab.new_game_2d(inputs['num_rows'], inputs['num_cols'],
                         inputs['bombs'])
    for name in expected:
        assert result[name] == expected[name]

def _do_test_2d_integration(test):
    """ dig, render, and render_2d_board on boards """
    exp_fname = os.path.join(TEST_DIRECTORY, 'test_outputs', f'test2d_integration_{test:02d}.pickle')
    inp_fname = os.path.join(TEST_DIRECTORY, 'test_inputs', f'test2d_integration_{test:02d}.pickle')
    with open(inp_fname, 'rb') as f:
        inputs = pickle.load(f)
    with open(exp_fname, 'rb') as f:
        expected = pickle.load(f)
    game = lab.new_game_2d(*inputs[0])
    for location, exp in zip(inputs[1], expected):
        num, g, render, renderx, ascii_, ascii_x = exp
        assert lab.dig_2d(game, *location) == num
        for key in g:
            assert game[key] == g[key]
        assert lab.render_2d_locations(game) == render
        assert lab.render_2d_locations(game, all_visible=True) == renderx
        assert lab.render_2d_board(game) == ascii_
        assert lab.render_2d_board(game, all_visible=True) == ascii_x

    last_state = game['state']
    if last_state in {'victory', 'defeat'}:
        for r in range(game['dimensions'][0]):
            for c in range(game['dimensions'][1]):
                assert lab.dig_2d(game, *location) == 0
                assert game['state'] == last_state
    else:
        for r in range(game['dimensions'][0]):
            for c in range(game['dimensions'][1]):
                if game['visible'][r][c]:
                    assert lab.dig_2d(game, *location) == 0
                    assert game['state'] == 'ongoing'


def test_2d_integration():
    for testnum in range(9):
        _do_test_2d_integration(testnum)


def test_newsmall6dgame():
    """ Testing new_game on a small 6-D board """
    exp_fname = os.path.join(TEST_DIRECTORY, 'test_outputs', 'testnd_newsmall6dgame.pickle')
    inp_fname = os.path.join(TEST_DIRECTORY, 'test_inputs', 'testnd_newsmall6dgame.pickle')
    with open(exp_fname, 'rb') as f:
        expected = pickle.load(f)
    with open(inp_fname, 'rb') as f:
        inputs = pickle.load(f)
    result = lab.new_game_nd(inputs['dimensions'], inputs['bombs'])
    for i in ('dimensions', 'board', 'visible', 'state'):
        assert result[i] == expected[i]


def test_newlarge4dgame():
    """ Testing new_game on a large 4-D board """
    exp_fname = os.path.join(TEST_DIRECTORY, 'test_outputs', 'testnd_newlarge4dgame.pickle')
    inp_fname = os.path.join(TEST_DIRECTORY, 'test_inputs', 'testnd_newlarge4dgame.pickle')
    with open(exp_fname, 'rb') as f:
        expected = pickle.load(f)
    with open(inp_fname, 'rb') as f:
        inputs = pickle.load(f)
    result = lab.new_game_nd(inputs['dimensions'], inputs['bombs'])
    for i in ('dimensions', 'board', 'visible', 'state'):
        assert result[i] == expected[i]


def test_tiny_dig_nd():
    # super tiny example 1D example
    F = False
    T = True
    game = lab.new_game_nd((3,), [(1,)])
    expected = {
        'dimensions': (3,),
        'state': 'ongoing',
        'board': [1, '.', 1],
        'visible': [F, F, F,],
    }
    for i in ('dimensions', 'board', 'visible', 'state'):
        assert game[i] == expected[i]

    assert lab.dig_nd(game, (2,)) == 1
    assert game['visible'] == [F, F, T]
    assert game['state'] == 'ongoing'

    expected_vis = [F, T, T]
    assert lab.dig_nd(game, (1,)) == 1
    assert game['visible'] == expected_vis
    assert game['state'] == 'defeat'

    # reset
    game = lab.new_game_nd((3,), [(1,)])
    assert lab.dig_nd(game, (0,)) == 1
    assert game['visible'] == [T, F, F]
    assert game['state'] == 'ongoing'

    assert lab.dig_nd(game, (0,)) == 0
    assert game['visible'] == [T, F, F]
    assert game['state'] == 'ongoing'

    assert lab.dig_nd(game, (2,)) == 1
    assert game['visible'] == [T, F, T]
    assert game['state'] == 'victory'

    assert lab.dig_nd(game, (1,)) == 0
    assert game['visible'] == [T, F, T]
    assert game['state'] == 'victory'

    # now test the dig behavior on a small 1D game
    game = lab.new_game_nd((10,), [(0,), (9,), (7,), (2,)])
    expected = {
        'dimensions': (10,),
        'state': 'ongoing',
        'board': ['.', 2, '.', 1, 0, 0, 1, '.', 2, '.'],
        'visible': [F, F, F, F, F, F, F, F, F, F],
    }
    for i in ('dimensions', 'board', 'visible', 'state'):
        assert game[i] == expected[i]

    # now let's dig!
    expected_vis = [F, T, F, F, F, F, F, F, F, F]
    assert lab.dig_nd(game, (1,)) == 1
    assert game['visible'] == expected_vis
    for i in ('dimensions', 'board', 'state'):
        assert game[i] == expected[i]

    expected_vis = [F, T, F, T, F, F, F, F, F, F]
    assert lab.dig_nd(game, (3,)) == 1
    assert game['visible'] == expected_vis
    for i in ('dimensions', 'board', 'state'):
        assert game[i] == expected[i]

    expected_vis = [F, T, F, T, T, T, T, F, F, F]
    assert lab.dig_nd(game, (4,)) == 3
    assert game['visible'] == expected_vis
    for i in ('dimensions', 'board', 'state'):
        assert game[i] == expected[i]

    # dig again
    for c in [1, 3, 4, 5, 6]:
        assert lab.dig_nd(game, (c,)) == 0
        assert game['visible'] == expected_vis
        for i in ('dimensions', 'board', 'state'):
            assert game[i] == expected[i]

    # win
    expected_vis =  expected_vis = [F, T, F, T, T, T, T, F, T, F]
    assert lab.dig_nd(game, (8,)) == 1
    assert game['visible'] == expected_vis
    assert game['state'] == 'victory'
    for i in ('dimensions', 'board'):
        assert game[i] == expected[i]

    # dig again
    for c in range(10):
        assert lab.dig_nd(game, (c,)) == 0
        assert game['visible'] == expected_vis
        assert game['state'] == 'victory'
        for i in ('dimensions', 'board'):
            assert game[i] == expected[i]

    #######################################################################
    # start over
    game = lab.new_game_nd((10,), [(0,), (9,), (7,), (2,)])
    for i in ('dimensions', 'board', 'visible', 'state'):
        assert game[i] == expected[i]

    # lose
    expected_vis =  [F, F, T, F, F, F, F, F, F, F]
    assert lab.dig_nd(game, (2,)) == 1
    assert game['visible'] == expected_vis
    assert game['state'] == 'defeat'
    for i in ('dimensions', 'board'):
        assert game[i] == expected[i]

    # dig again
    for c in range(10):
        assert lab.dig_nd(game, (c,)) == 0
        assert game['visible'] == expected_vis
        assert game['state'] == 'defeat'
        for i in ('dimensions', 'board'):
            assert game[i] == expected[i]



@pytest.mark.parametrize('test', [1,2,3])
def test_nd_integration(test):
    exp_fname = os.path.join(TEST_DIRECTORY, 'test_outputs', f'testnd_integration{test}.pickle')
    inp_fname = os.path.join(TEST_DIRECTORY, 'test_inputs', f'testnd_integration{test}.pickle')
    with open(exp_fname, 'rb') as f:
        expected = pickle.load(f)
    with open(inp_fname, 'rb') as f:
        inputs = pickle.load(f)
    g = lab.new_game_nd(inputs['dimensions'], inputs['bombs'])
    for location, results in zip(inputs['digs'], expected):
        squares_revealed, game, rendered, rendered_all_visible = results
        res = lab.dig_nd(g, location)
        assert res == squares_revealed
        for i in ('dimensions', 'board', 'visible', 'state'):
            assert g[i] == game[i]
        assert lab.render_nd(g) == rendered
        assert lab.render_nd(g, True) == rendered_all_visible

    # dig again
    res = lab.dig_nd(g, location)
    assert res == 0
    for i in ('dimensions', 'board', 'visible', 'state'):
        assert g[i] == game[i]
    assert lab.render_nd(g) == rendered
    assert lab.render_nd(g, True) == rendered_all_visible

    # lose
    if g['state'] == 'ongoing':
        res = lab.dig_nd(g, inputs['bombs'][0])
        assert res == 1
        assert g['state'] == 'defeat'




def test_doctests_run():
    """ Checking to see if all lab doctests run successfully """
    results = doctest.testmod(lab, optionflags=TESTDOC_FLAGS, report=False)
    num_failed, num_run = results
    assert num_failed == 0 and num_run > 0
