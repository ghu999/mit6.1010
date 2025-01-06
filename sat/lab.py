"""
6.101 Lab:
SAT Solver
"""

#!/usr/bin/env python3

# import typing  # optional import
# import pprint  # optional import
import doctest
import sys

sys.setrecursionlimit(10_000)
# NO ADDITIONAL IMPORTS


def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> T, F = True, False
    >>> x = satisfying_assignment([[('a', T), ('b', F), ('c', T)]])
    >>> x.get('a', None) is T or x.get('b', None) is F or x.get('c', None) is T
    True
    >>> satisfying_assignment([[('a', T)], [('a', F)]])
    """
    def recur(formula, assignments):
        if not formula:
            return assignments
        if [] in formula:
            return None
        for clause in formula:
            if len(clause) == 1:
                updated = update_expression(formula, [(clause[0][0], clause[0][1])])
                new_assignments = assignments.copy()
                new_assignments[clause[0][0]] = clause[0][1]
                return recur(updated, new_assignments)
        var = formula[0][0][0]
        for val in [True, False]:
            updated = update_expression(formula, [(var, val)])
            new_assignments = assignments.copy()
            new_assignments[var] = val
            result = recur(updated, new_assignments)
            if result is not None:
                return result
        return None
    return recur(formula, {})

def update_expression(formula, conditions):
    """
    Updates the expression given each condition whether a variable
    is set to True or False.
    """
    lookup = dict(conditions)
    result = []
    for clause in formula:
        new_clause = []
        satisfied = False
        for exp, val in clause:
            if exp in lookup:
                if val == lookup[exp]:
                    satisfied = True
                    break
            else:
                new_clause.append((exp, val))

        if not satisfied:
            result.append(new_clause)
    return result


def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz-room-scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a set
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """
    final_rule = []
    #rule 1
    for rule in rule1(student_preferences):
        final_rule.append(rule)
    #rule 2
    room_list = list(room_capacities.keys())
    for rule in rule2(student_preferences, room_list):
        final_rule.append(rule)
    #rule3
    name_list = list(student_preferences.keys())
    for location in room_capacities:
        if room_capacities[location] < len(student_preferences):
            for clause in rule3(name_list, room_capacities[location]+1, location):
                final_rule.append(clause)

    return final_rule

def rule1(student_preferences):
    result = []
    for name in student_preferences:
        clause = []
        for room in student_preferences[name]:
            clause.append((str(name)+"_"+str(room), True))
        result.append(clause)
    return result

def rule2(student_preferences, room_list):
    result = []
    for person in student_preferences:
        for i in range(len(room_list)):
            for j in range(i+1, len(room_list)):
                room1, room2 = room_list[i], room_list[j]
                result.append([(str(person)+"_"+str(room1), False),
                                   (str(person)+"_"+str(room2), False)])
    return result
def rule3(name_list, n, location):
    if n == 0:
        return [[]]
    if n > len(name_list):
        return []
    result = []
    for i in range(len(name_list)):
        for combo in rule3(name_list[i+1:], n-1, location):
            result.append([(name_list[i]+"_"+str(location), False)] + combo)
    return result


if __name__ == "__main__":
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)

    # formula = [
    # [('a', True), ('b', True), ('c', True)],
    # [('a', False), ('f', True)],
    # [('d', False), ('e', True), ('a', True), ('g', True)],
    # [('h', False), ('c', True), ('a', False), ('f', True)],
    # ]
    #print(update_expression(formula, [('a', True), ('f', False)]))
    #print(possible_vars(formula))
    #print(satisfying_assignment(formula))
