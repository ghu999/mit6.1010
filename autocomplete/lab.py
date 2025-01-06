"""
6.101 Lab:
Autocomplete
"""

# NO ADDITIONAL IMPORTS!

# import string # optional import
# import pprint # optional import
# import typing # optional import
import doctest
from text_tokenize import tokenize_sentences


class PrefixTree:
    """
    A prefix tree is a type of tree that 
    stores an associative array (a mapping from keys to values)
    """
    def __init__(self):
        self.value = None
        self.children = {}

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the prefix tree,
        or reassign the associated value if it is already present.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError
        if len(key) == 0:
            self.value = value
        else:
            letter = key[0:1]
            if letter not in self.children:
                self.children[letter] = PrefixTree()
            self.children[letter].__setitem__(key[1:], value)

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        >>> tree = PrefixTree()
        >>> tree['bat'] = 7
        >>> tree['bark'] = ':)'
        >>> tree['bark']
        ':)'
        >>> tree['ba']
        """
        if not isinstance(key, str):
            raise TypeError
        for letter in key:
            if letter not in self.children:
                raise KeyError
            self = self.children[letter]
        if self.value is None:
            raise KeyError
        return self.value

    def __delitem__(self, key):
        """
        Delete the given key from the prefix tree if it exists.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError
        if len(key) == 0:
            if self.value is None:
                raise KeyError
            self.value = None
        else:
            letter = key[0:1]
            if letter not in self.children:
                raise KeyError
            self.children[letter].__delitem__(key[1:])

    def __contains__(self, key):
        """
        Is key a key in the prefix tree?  Return True or False.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError
        if len(key) == 0:
            if self.value is None:
                return False
            return True
        if key[0] not in self.children:
            return False
        else:
            return self.children[key[0]].__contains__(key[1:])

    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values in this prefix tree
        and its children.  Must be a generator!
        """
        def recur(pt, prefix):
            if pt.value is not None:
                yield (prefix, pt.value)
            for ch, child in pt.children.items():
                yield from recur(child, prefix + ch)
        return recur(self, "")
    def subtree(self, prefix):
        """
        Returns the subtree of the prefix (what is left)
        """
        if len(prefix) == 0:
            return self
        if prefix[0] not in self.children:
            return PrefixTree()
        if len(prefix) == 1:
            return self.children[prefix]
        else:
            return self.children[prefix[0]].subtree(prefix[1:])
    def edits(self, prefix):
        """
        Returns all possible valid edits to a word
        """
        result = set()
        alphabet = "abcdefghijklmnopqrstuvwxyz"

        for i in range(len(prefix)):
            #insertion and replacement
            for char in alphabet:
                insert = prefix[0:i] + char + prefix[i:]
                if insert in self:
                    result.add((self[insert], insert))
                replace = prefix[0:i] + char + prefix[i+1:]
                if replace in self:
                    result.add((self[replace], replace))
            #deletion
            delete = prefix[0:i] + prefix[i+1:]
            if delete in self:
                result.add((self[delete], delete))
            #transpose
            if i < len(prefix) - 1:
                transpose = prefix[0:i] + prefix[i+1] + prefix[i] + prefix[i+2:]
                if transpose in self:
                    result.add((self[transpose], transpose))
        if prefix in self:
            print("prefix in self")
            result.remove((self[prefix], prefix))
        return result

def word_frequencies(text):
    """
    Given a piece of text as a single string, create a prefix tree whose keys
    are the words in the text, and whose values are the number of times the
    associated word appears in the text.
    """
    sentence_strings = tokenize_sentences(text)
    vals = {}
    for sentence in sentence_strings:
        for word in sentence.split(" "):
            if word in vals:
                vals[word] += 1
            else:
                vals[word] = 1
    tree = PrefixTree()
    for word,val in vals.items():
        tree[word] = val
    return tree

def autocomplete(tree, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is not a string.
    """
    if not isinstance(prefix, str):
        raise TypeError
    subtree = tree.subtree(prefix)
    sorted_list = sorted([(val, prefix + suffix)
                          for suffix, val in subtree], reverse=True)
    result = []
    for tup in sorted_list:
        if max_count is not None:
            if len(result) >= max_count:
                break
        result.append(tup[1])
    return result
def autocorrect(tree, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """
    result = autocomplete(tree, prefix, max_count)
    if max_count is not None and len(result) == max_count:
        return result
    all_edits = tree.edits(prefix)
    sort = sorted(all_edits, key=lambda x: x[0], reverse=True)
    sorted_edits = []
    sorted_edits = [key for _, key in sort]
    while sorted_edits and (max_count is None or len(result) < max_count):
        result.append(sorted_edits.pop(0))
    return result


def word_filter(tree, pattern):
    """
    Return list of (word, freq) for all words in the given prefix tree that
    match pattern.  pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    def recursive(tree, prefix):
        if len(prefix) == 0:
            if tree.value is not None:
                return [(prefix, tree.value)]
            else:
                return []
        result = []
        if prefix[0] == "?":
            for letter in tree.children:
                out = recursive(tree.children[letter], prefix[1:])
                out = [(letter + pat, value) for pat, value in out]
                result.extend(out)
        elif prefix[0] == "*":
            result.extend(recursive(tree, prefix[1:]))
            for letter in tree.children:
                out = recursive(tree.children[letter], prefix)
                out = [(letter + pat, value) for pat, value in out]
                result.extend(out)
        else:
            if prefix[0] in tree.children:
                out = recursive(tree.children[prefix[0]], prefix[1:])
                out = [(prefix[0] + pat, value) for pat, value in out]
                result.extend(out)
        return result
    final_result = list(set(recursive(tree, pattern)))
    return final_result

if __name__ == "__main__":
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests
    # doctest.run_docstring_examples( # runs doctests for one function
    #    PrefixTree.__getitem__,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=True
    # )
    with open("meta.txt", encoding="utf-8") as f:
        meta = f.read()
    metatree = word_frequencies(meta)
    print(autocomplete(metatree, "gre", 6))
    print(word_filter(metatree, "c*h"))

    with open("cities.txt", encoding="utf-8") as f:
        cities = f.read()
    citiestree = word_frequencies(cities)
    print(word_filter(citiestree, "r?c*t"))

    with open("alice.txt", encoding="utf-8") as f:
        alice = f.read()
    alicetree = word_frequencies(alice)
    print(autocorrect(alicetree, "hear", 12))

    with open("pride.txt", encoding="utf-8") as f:
        pride = f.read()
    pridetree = word_frequencies(pride)
    print(autocorrect(pridetree, "hear"))

    with open("dracula.txt", encoding="utf-8") as f:
        dracula = f.read()
    draculatree = word_frequencies(dracula)
    draculafilter = word_filter(draculatree, '*')
    print(len(draculafilter))
    total = 0
    for pair in draculafilter:
        sum += pair[1]
    print(total)
