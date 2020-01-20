
import os
import sys

bspath = os.path.join(os.path.dirname(os.path.abspath(
    __file__)), "libraries/backports.functools_lru_cache-1.6.1")
sys.path.append(bspath)
bspath = os.path.join(os.path.dirname(os.path.abspath(
    __file__)), "libraries/beautifulsoup4-4.8.0")
sys.path.append(bspath)
bspath = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "libraries/soupsieve-1.9.5")
sys.path.append(bspath)

import requests
from bs4 import BeautifulSoup
from data_diff import Diff
import codecs
import json
import soupsieve
import bs4
import backports.functools_lru_cache
import io
import re

# this should be in one place


def json_load_byteified(file_handle):
    return _byteify(
        json.load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )


def _byteify(data, ignore_dicts=False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [_byteify(item, ignore_dicts=True) for item in data]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data


def shouldUpdateRelease(candidatePath, releasePath):
    candidate = None
    release = None
    try:
        candidate = unicode(json_load_byteified(open(candidatePath)))
    except (ValueError, IOError):
        print('no cadidate')
        return False
    try:
        release = unicode(json_load_byteified(open(releasePath)))
    except (ValueError, IOError):
        print('no release')
        return True
    print ('comparing')
    return candidate != release


# first = json_load_byteified(open('candidates/people.json'))

# second = json_load_byteified(open('releases/people.json'))

# fstring = unicode(first)
# fsecond = unicode(second)
# print(fstring)
# print('***')
# print(second)
# print('***')
# print(fstring == fsecond)
