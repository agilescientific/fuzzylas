#################################
# Import stuff
import levenshtein
import logging
import process
from google.appengine.api import memcache
from google.appengine.api import search

#################################
# Pre-populate the memcache
# Do 10 TLA's first
# All of them will be about 17000 items, should take a while!
# How to not lock up the app while it does this?

#################################
# Various guessing algorithms

# Levenshtein guess
def guess_simple(data,word,lim):
    words = []
    distances = []
    smallest = 100
    for w in data.keys():
        distance = levenshtein.levenshtein(word,w)
        if distance <= smallest:
            words.insert(0,w)
            distances.insert(0,distance)
            smallest = distance
        else:
            words.append(str(w))
            distances.append(distance)

    output = {}
    for i in range(lim):
        output[words[i]] = data[words[i]]
        i += 1

    return output

# Try another way to step over dict
def guess_simple2(data,word,lim):
    words = []
    distances = []
    smallest = 100
    for w in data:
        distance = levenshtein.levenshtein(word,w)
        if distance <= smallest:
            words.insert(0,w)
            distances.insert(0,distance)
            smallest = distance
        else:
            words.append(str(w))
            distances.append(distance)

    output = {}
    for i in range(lim):
        output[words[i]] = data[words[i]]
        i += 1

    return output

# Try yet another way to step over dict
def guess_simple3(data,word,lim):
    words = []
    distances = []
    smallest = 100
    for w in data:
        distance = levenshtein.levenshtein2(word,w)
        if distance <= smallest:
            words.insert(0,w)
            distances.insert(0,distance)
            smallest = distance
        else:
            words.append(str(w))
            distances.append(distance)

    output = {}
    for i in range(lim):
        output[words[i]] = data[words[i]]
        i += 1

    key = word + '-' + 'simple' + '-' + str(lim) 
    memcache.set(key,output)

    return output

# Fuzzywuzzy guess
def guess_fuzzy(data,word,lim):
    hits = process.extract(word,data.keys(),limit=lim)

    output = {}
    for hit in hits:
        output[(hit[1],hit[0])] = data[hit[0]]

    key = word + '-' + 'fuzzy' + '-' + str(lim) 
    memcache.set(key,output)

    return output
    
# def guess_search(word,lim):
#     
#     index = search.Index(name='curves')
#     
#     query = "{0}".format(word)
#     #query = "mnemonic = {0}".format(word)
# 
#     result = []
# 
#     try:
#         results = index.search(search.Query(
#             query_string=query,
#             options=search.QueryOptions(
#                 limit=lim,
#                 returned_fields=['mnemonic', 'company', 'units']
#                 )
#             ))
# 
#         return results
# 
#     except search.Error:
#         logging.exception('Search failed; do something with this error')
    
#################################
# Main guess routine - calls one of the others
# curves dataset, input, method, guesses
def guess(data,word,method,lim):

    key = word + '-' + method + '-' + str(lim) 
    guess = memcache.get(key)
    
    if guess is None:

        if word in data:
            return {word: data[word]}
        elif method == "exact":
            return None   # we only get this if there's no match
        elif method == "simple":
            return guess_simple3(data,word,lim)
#         elif method == "search":
#             return guess_search(word,lim)
        else:
            return guess_fuzzy(data,word,lim)

    else:
        return guess
            