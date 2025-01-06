"""
6.101 Lab:
Bacon Number
"""

#!/usr/bin/env python3

import pickle
# import typing # optional import
# import pprint # optional import

# NO ADDITIONAL IMPORTS ALLOWED!

def transform_data(raw_data):
    """
    Given the raw data in the form [(actor1, actor2, film)],
    return 2 dictionaries. First dictionary is in the form
    {actor: {neighbor1, neighbor2, etc.}, actor2, etc.} Second
    dictionary is in the form {movieid: {actor1, actor2, etc.},
    movieid2, etc.}
    """
    dictionary = {}
    #print(raw_data)
    movie_dict = {}
    for tup in raw_data:
        a1 = tup[0]
        a2 = tup[1]
        movie_id = tup[2]
        if a1 not in dictionary:
            dictionary[a1] = set([a2])
        else:
            dictionary[a1].add(a2)
        if a2 not in dictionary:
            dictionary[a2] = set([a1])
        else:
            dictionary[a2].add(a1)
        if movie_id not in movie_dict:
            movie_dict[movie_id] = set([])
            movie_dict[movie_id].add(a1)
            movie_dict[movie_id].add(a2)
        else:
            movie_dict[movie_id].add(a1)
            movie_dict[movie_id].add(a2)
    for actor in dictionary:
        actor = list(dictionary[actor])
    return (dictionary, movie_dict)

def acted_together(transformed_data, actor_id_1, actor_id_2):
    """
    Returns True if actor_id_1 has worked in the same movie as
    actor_id_2.
    """
    if actor_id_1 == actor_id_2: return True
    if (actor_id_1 not in transformed_data[0].keys() or
        actor_id_2 not in transformed_data[0].keys()):
        return False
    if (actor_id_2 in transformed_data[0][actor_id_1]
    and actor_id_1 in transformed_data[0][actor_id_2]):
        return True
    return False

def actors_with_bacon_number(transformed_data, n):
    """
    Returns a Python set containing the ID numbers
    of all the actors with that Bacon number.
    Note that we'll define the Bacon number to be 
    the smallest number of films separating
    a given actor from Kevin Bacon, whose actor
    ID is 4724.
    """
    if n == 0:
        return set([4724])
    if n == 1:
        #print(transformed_data[4724])
        return set(transformed_data[0][4724])
    queue = [(4724, 0)] #queue
    visited = set([]) #the visited list to not cause infinite loop
    bacon = {0:visited} #number:actor
    while queue:
        actor = queue.pop(0) #pop first
        if actor[0] not in visited: #if not visited
            visited.add(actor[0])
            if actor[1] not in bacon: #set in bacon
                bacon[actor[1]] = set([actor[0]])
            else:
                bacon[actor[1]].add(actor[0])
            for vals in transformed_data[0][actor[0]]: #add all neighbors
                queue.append((vals, actor[1]+1)) #add neighbors:n+1
    if n not in bacon:
        return set([])
    return bacon[n]

def bacon_path(transformed_data, actor_id):
    """
    Finds a bacon path from 4724 to the given actor id
    """
    return actor_to_actor_path(transformed_data, 4724, actor_id)

def actor_to_actor_path(transformed_data, actor_id_1, actor_id_2):
    """
    Finds the smallest path connecting two actors actor_id_1 and
    actor_id_2.
    """
    return(actor_path(transformed_data, actor_id_1, lambda x: x == actor_id_2))

def movie_info(raw_data):
    """
    Given the raw data in the form [(actor1, actor2, film)],
    return a dictionary in the form {actor: {(neighbor, film)}}.
    """
    dictionary = {}
    for tup in raw_data:
        a1 = tup[0]
        a2 = tup[1]
        movie_id = tup[2]
        if a1 not in dictionary:
            dictionary[a1] = [(a2, movie_id)]
        else:
            dictionary[a1].append([a2, movie_id])
        if a2 not in dictionary:
            dictionary[a2] = [(a1, movie_id)]
        else:
            dictionary[a2].append([a1, movie_id])
    for actor in dictionary.items():
        actor = list(dictionary[actor])
    return dictionary

def movie_links(raw_data, actor1, actor2):
    """
    Determines if an actor worked in the same movie
    as actor1
    """
    movie = movie_info(raw_data)
    list_movies = movie[actor1]
    for tup in list_movies:
        if tup[0] == actor2:
            return tup[1]
    return -1

def movie_paths(transformed_data, raw_data, movies_dict, names_dict, name1, name2):
    """
    Determines a path through movies from two names. 
    After finding the path, converts the movie path list with IDs
    back to the movie names.
    """
    actor_id_1 = names_dict[name1]
    actor_id_2 = names_dict[name2]
    path = actor_to_actor_path(transformed_data, actor_id_1, actor_id_2)
    movie_path = []
    for i in range(0, len(path)-1):
        movie_path.append((list(movies_dict.keys())
            [list(movies_dict.values())
            .index(movie_links(raw_data, path[i], path[i+1]))]))
    return movie_path

def actor_path(transformed_data, actor_id_1, goal_test_function):
    """
    A more general form of actor to actor path. Given any arbitrary
    function, if the actor satisfies the function, finds a path given the actor.
    """
    if goal_test_function(actor_id_1):
        return [actor_id_1]
    path = []
    visited = set()
    queue = [[actor_id_1]]
    while queue:
        path = queue.pop(0)
        for neighbor in transformed_data[0][path[-1]]:
            if goal_test_function(neighbor):
                path.append(neighbor)
                return path
            if neighbor not in visited:
                new_path = path.copy()
                new_path += [neighbor]
                queue.append(new_path)
            visited.add(neighbor)
    return None

def actors_connecting_films(transformed_data, film1, film2):
    """
    Finds the shortest path connecting two films using the second
    element of transformed_data and calling actor_path in order
    to use the internally defined function infilm.
    """
    movie_dict = transformed_data[1]
    min_length = 1000000
    result = None
    def infilm(actor):
        if actor in movie_dict[film2]:
            return True
        return False
    if film1 not in movie_dict or film2 not in movie_dict:
        return None
    for actor in movie_dict[film1]:
        path = actor_path(transformed_data, actor, infilm)
        if not path:
            continue
        if len(path) < min_length:
            result = path
            min_length = len(path)
    return result


if __name__ == "__main__":
    with open("resources/small.pickle", "rb") as f:
        smalldb = pickle.load(f)

    with open("resources/names.pickle", "rb") as f:
        names = pickle.load(f)

    with open("resources/tiny.pickle", "rb") as f:
        tinydb = pickle.load(f)

    with open("resources/large.pickle", "rb") as f:
        largedb = pickle.load(f)

    with open("resources/movies.pickle", "rb") as f:
        movies = pickle.load(f)
    #print(tinydb)
    print(transform_data(tinydb)[1])
    #print(actors_with_bacon_number(transform_data(tinydb), 2))
    #print(smalldb["Bruce McCulloch"])
    #print(list(smalldb.keys())[list(smalldb.values()).index(142752)])
    #transformed = transform_data(smalldb)
    #print(names)
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    # print(acted_together(transformed, names["Dean Paraskevopoulos"],
    # names["David Stevens"]))
    #print(names["Dean Paraskevopoulos"], names["David Stevens"])
    #------------------
    # print(names["Louise Devar"], names["Stephanie Sotomayer"])
    # print(acted_together(transformed, names["Louise Devar"],
    # names["Stephanie Sotomayer"]))
    #------------------
    #actors = (actors_with_bacon_number(transform_data(largedb), 6))
    # actors = {1367972, 1345461, 1345462, 1338716}
    # for actor in actors:
    #     print((list(names.keys())[list(names.values()).index(actor)]))
    #------------------
    #print(bacon_path(transform_data(largedb), names["Edward Biby"]))
    # actors = [4724, 4610, 102429, 30195, 89600, 1395666]
    # for actor in actors:
    #     print((list(names.keys())[list(names.values()).index(actor)]))
    #------------------
    # print(actor_to_actor_path(transform_data(largedb),
    # names["Alydra Kelly"], names["Toi Svane Stepp"]))
    # actors = [1019969, 933065, 16660, 33155, 6908, 945237]
    # for actor in actors:
    #      print((list(names.keys())[list(names.values()).index(actor)]))
    #------------------
    #print(movie_info(tinydb))
    # print(movie_paths(transform_data(tinydb), tinydb, movies, names,
    #         "Kevin Bacon", (list(names.keys())[list(names.values()).index(1532)])))
    #print(movie_paths(transform_data(largedb), largedb, movies, names,
             #"Blair Brown", "Sven Batinic"))
    #------------------
    #print(actors_connecting_films(transform_data(largedb), 18860, 75181))
    pass
