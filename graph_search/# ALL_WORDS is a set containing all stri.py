#GRAPH SEARCH
# ALL_WORDS is a set containing all strings that should be considered valid
# words (all in lower-case)
with open('words.txt') as f:
    ALL_WORDS = {i.strip() for i in f}

# replace the following with the starting state
start_state = "patties"

# replace this neighbors function:
def word_ladder_neighbors(state):
    """
    takes a state as input
    returns all neighboring states (valid words that differ in one letter)
    """
    letters = []
    neighbors = []
    print(state)
    for letter in state:
        letters.append(ord(letter) - 97)
    print(f"{letters=}")
    for i in range(len(letters)):
        letter = letters[i]
        for j in range(1, 26):
            letters_copy = letters.copy()
            letters_copy[i] = ((letter + j) % 26)
            word = ""
            for k in range(len(letters_copy)):
                word += chr(letters_copy[k] + 97)
            if word in ALL_WORDS:
                neighbors.append(word)
    print(f"{neighbors=}")
    return neighbors

# replace this goal test function:
def goal_test_function(state):
    """
    takes a state as input
    returns True if and only if state matches the goal (the target word)
    """
    if state == "foaming":
        return True
    return False

def find_path(word_ladder_neighbors, start_state, goal_test_function):
    if goal_test_function(start_state):
        return (start_state,)
    agenda = [(start_state,)]
    visited = {start_state}

    while agenda:
        this_path = agenda.pop(0)
        terminal_state = this_path[-1]

        for neighbor in word_ladder_neighbors(terminal_state):
            if neighbor not in visited:
                new_path = this_path + (neighbor,)

                if goal_test_function(neighbor):
                    return new_path

                agenda.append(new_path)
                visited.add(neighbor)
    return None

# ultimately, these variables will be passed as arguments to the find_path
# function to solve for the path between "patties" and "foaming"
#
output = find_path(word_ladder_neighbors, start_state, goal_test_function)
print(output)
