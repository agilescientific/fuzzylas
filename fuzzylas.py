#!/usr/bin/env python
# -*- coding: utf-8 -*-

import levenshtein
import process
from google.appengine.api import memcache
# from google.appengine.api import search

from utils import flatten_list

#################################
# TODO
# Pre-populate the memcache
# Do 10 TLA's first
# All of them will be about 17000 items, should take a while!
# How to not lock up the app while it does this?

#################################
# Various guessing algorithms


def guess_simple(data, word, limit=-1, maxdist=1):
    """
    Another way to step over dict.

    Args:
        limit (int): the max number of items to return. We don't use it here.
        maxdist (int): the max allowed edit distance. We only use that.
    """
    output = []
    for w, curves in data.items():
        d = levenshtein.levenshtein2(word, w)
        if d <= maxdist:
            for c in curves:
                if not c['mnemonic']: continue
                result = {"distance": d, "mnemonic": w, "curve": c}
                output.append(result)


    key = word + '-' + 'simple' + '-' + str(limit) + str(maxdist)
    memcache.set(key, output)

    return output


def guess_fuzzy(data, word, limit=1, maxdist=1):
    """
    Fuzzywuzzy guess

    Args:
        limit (int): the max number of items to return.
        maxdist (int): the max allowed edit distance.
    """
    hits = process.extract(word, data.keys(), limit=limit)

    output = []
    for w, s in hits:
        d = levenshtein.levenshtein2(word, w)
        if d > maxdist:
            continue
        curves = data[w]
        for c in curves:
            result = {"distance": d,
                      "score": s,
                      "mnemonic": w,
                      "curve": c}
            output.append(result)
    key = word + '-' + 'fuzzy' + '-' + str(limit) + str(maxdist)
    memcache.set(key, output)

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


def guess(data, word, method, limit, maxdist):
    """
    Main guess routine - calls one of the others
    curves dataset, input, method, limit, maxdist
    """
    limit = int(limit)
    maxdist = int(maxdist)
    key = word + '-' + method + '-' + str(limit)
    g = memcache.get(key)

    if g is None:

        if word in data:
            return {word: data[word]}
        elif method == "exact":
            return None
        elif method == "simple":
            return guess_simple(data, word, limit, maxdist)
        else:
            return guess_fuzzy(data, word, limit, maxdist)

    else:
        return g
