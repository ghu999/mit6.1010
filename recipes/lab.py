"""
6.101 Lab:
Recipes
"""

import pickle
import sys
# import typing # optional import
# import pprint # optional import
sys.setrecursionlimit(20_000)
# NO ADDITIONAL IMPORTS!


def atomic_ingredient_costs(recipes_db):
    """
    Given a recipes database, a list containing compound and atomic food tuples,
    make and return a dictionary mapping each atomic food name to its cost.
    """
    recipes = {}
    for tup in recipes_db:
        if tup[0] == 'atomic':
            recipes[tup[1]] = tup[2]
    return recipes

def compound_ingredient_possibilities(recipes_db):
    """
    Given a recipes database, a list containing compound and atomic food tuples,
    make and return a dictionary that maps each compound food name to a
    list of all the ingredient lists associated with that name.
    """
    recipes = {}
    for tup in recipes_db:
        if tup[0] == 'compound':
            if tup[1] not in recipes:
                recipes[tup[1]] = [tup[2]]
            else:
                recipes[tup[1]].append(tup[2])
    return recipes

def lowest_cost(recipes_db, food_name, forbidden=None):
    """
    Given a recipes database and the name of a food (str), return the lowest
    cost of a full recipe for the given food item or None if there is no way
    to make the food_item.
    """
    atomic = atomic_ingredient_costs(recipes_db)
    compound = compound_ingredient_possibilities(recipes_db)
    def recur(food):
        if forbidden is not None and food in forbidden:
            return None
        if food not in atomic and food not in compound:
            return None
        min_cost = float("inf")
        if food in atomic:
            return atomic[food]
        for ingredients in compound[food]:
            total = 0
            for ingredient, amt in ingredients:
                cost = recur(ingredient)
                #print(ingredient, amt, cost)
                if cost is None:
                    total = float("inf")
                    break
                total += cost * amt
            min_cost = min(min_cost, total)
        if min_cost == float("inf"):
            return None
        else:
            return min_cost
    return recur(food_name)

def scaled_recipe(recipe_dict, n):
    """
    Given a dictionary of ingredients mapped to quantities needed, returns a
    new dictionary with the quantities scaled by n.
    """
    scaled = {}
    for food in recipe_dict:
        scaled[food] = n * recipe_dict[food]
    return scaled


def add_recipes(recipe_dicts):
    """
    Given a list of recipe dictionaries that map food items to quantities,
    return a new dictionary that maps each ingredient name
    to the sum of its quantities across the given recipe dictionaries.

    For example,
        add_recipes([{'milk':1, 'chocolate':1}, {'sugar':1, 'milk':2}])
    should return:
        {'milk':3, 'chocolate': 1, 'sugar': 1}
    """
    result = {}
    for recipe in recipe_dicts:
        for food in recipe:
            if food in result:
                result[food] += recipe[food]
            else:
                result[food] = recipe[food]
    return result

def cheapest_flat_recipe(recipes_db, food_name, forbidden=None):
    """
    Given a recipes database and the name of a food (str), return a dictionary
    (mapping atomic food items to quantities) representing the cheapest full
    recipe for the given food item.

    Returns None if there is no possible recipe.
    """
    atomic = atomic_ingredient_costs(recipes_db)
    compound = compound_ingredient_possibilities(recipes_db)
    def recur(food):
        if forbidden and food in forbidden:
            return None
        if food in atomic:
            return {food: 1}
        min_cost = float("inf")
        best_recipe = None
        if food in compound:
            for ingredients in compound[food]:
                total = 0
                valid = True
                curr_recipe = []
                for ingredient, amt in ingredients:
                    cost = lowest_cost(recipes_db, ingredient, forbidden)
                    if forbidden and ingredient in forbidden or cost is None:
                        valid = False
                        break
                    total += cost * amt
                    flat = recur(ingredient)
                    if not flat:
                        valid = False
                        break
                    scaled = scaled_recipe(flat, amt)
                    curr_recipe.append(scaled)
                if valid and total < min_cost:
                    min_cost = total
                    best_recipe = curr_recipe
            if best_recipe:
                return add_recipes(best_recipe)
        return None
    return recur(food_name)

def combine_recipes(nested_recipes):
    """
    Given a list of lists of recipe dictionaries, where each inner list
    represents all the recipes for a certain ingredient, compute and return a
    list of recipe dictionaries that represent all the possible combinations of
    ingredient recipes.
    """
    def recur(recipes):
        if len(recipes) == 0:
            return []
        if len(recipes) == 1:
            return [recipe for recipe in recipes[0]]
        rest_recipes = recur(recipes[1:])
        result = []
        for recipe in recipes[0]:
            for combo in rest_recipes:
                combined = [recipe, combo]
                combined = add_recipes(combined)
                result.append(combined)
        return result
    return recur(nested_recipes)

def all_flat_recipes(recipes_db, food_name, forbidden=None):
    """
    Given a recipes database, the name of a food (str), produce a list (in any
    order) of all possible flat recipe dictionaries for that category.

    Returns an empty list if there are no possible recipes
    """
    atomic = atomic_ingredient_costs(recipes_db)
    compound = compound_ingredient_possibilities(recipes_db)
    result = {}
    def recur(food):
        if forbidden and food in forbidden:
            return []
        if food not in atomic and food not in compound:
            return []
        if food in atomic:
            return [{food:1}]
        flat_recipes = []
        if food in compound:
            for ingredients in compound[food]:
                curr_recipe = []
                for ingredient, amt in ingredients:
                    if forbidden and ingredient in forbidden:
                        curr_recipe = []
                        break
                    #print(f"{ingredient=}", f"{amt=}")
                    flat = recur(ingredient)
                    if not flat:
                        curr_recipe = []
                        break
                    scaled = []
                    #print(f"{flat=}")
                    for sub in flat:
                        scaled_rec = {
                            ing : quant * amt
                            for ing, quant in sub.items()
                        }
                        scaled.append(scaled_rec)
                    curr_recipe.append(scaled)
                    #print(f"{curr_recipe=}")
                if curr_recipe:
                    combined = combine_recipes(curr_recipe)
                    flat_recipes.extend(combined)
                    #print("flat recipes after extended", flat_recipes)

            if flat_recipes:
                result[food] = flat_recipes
            #print(f"{flat_recipes=}")
            return flat_recipes
    all_recipes = []
    recipes = recur(food_name)
    all_recipes.extend(recipes)
    return all_recipes


if __name__ == "__main__":
    # load example recipes from section 3 of the write-up
    with open("test_recipes/example_recipes.pickle", "rb") as f:
        example_recipes_db = pickle.load(f)
    # you are free to add additional testing code here!
    #count = 0
    #distinct_compound = set()
    #for tup in example_recipes_db:
        # if tup[0] == 'atomic':
        #     count+= 1
        # if tup[0] == 'compound':
        #     distinct_compound.add(tup[1])
    #print(count)
    #print(len(distinct_compound))
    atom = atomic_ingredient_costs(example_recipes_db)
    # total = 0
    # for item in atomic:
    #     total += atomic[item]
    # print(total)
    comp = compound_ingredient_possibilities(example_recipes_db)
    #print(atomic)
    #print(compound['ketchup'])
    # multiples = 0
    # print(compound)
    # for item in compound:
    #     if len(compound[item]) > 1:
    #         multiples += 1
    # print(multiples)
    #print(lowest_cost(example_recipes_db, 'burger'))
    dairy_recipes_db = [
    ('compound', 'milk', [('cow', 1), ('milking stool', 1)]),
    ('compound', 'cheese', [('milk', 1), ('time', 1)]),
    ('compound', 'cheese', [('cutting-edge laboratory', 11)]),
    ('atomic', 'milking stool', 5),
    ('atomic', 'cutting-edge laboratory', 1000),
    ('atomic', 'time', 10000),
    ('atomic', 'cow', 100),
    ]
    spreads_db = [
    ('atomic', 'peanut butter', 1),
    ('atomic', 'almond butter', 5),
    ('atomic', 'grape jelly', 2),
    ('compound', 'savory', [('peanut butter', 1)]),
    ('compound', 'savory', [('almond butter', 1)]),
    ('compound', 'sweet', [('grape jelly', 1)]),
    ('compound', 'sweet and salty', [('savory', 2), ('sweet', 2)]),
    ]
    #print(cheapest_flat_recipe(dairy_recipes_db, 'cheese'))
    # for line in spreads_db:
    #     print(line)
    print(all_flat_recipes(spreads_db, 'sweet and salty'))
