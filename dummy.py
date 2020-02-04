# Algorithm


# 1. go through the configs to generate candidates/
# 2. load version json
# 3. foreach item in config:
#   a. try to get the release
#     - if release fails candidate IS release
#   b. compare candidate & release
#     - if not not same, candidate is release:
#       --> copy file in releases/
#       --> increase versioning for module
#

# -*- coding: utf-8 -*-
from diff_check import shouldUpdateRelease, json_load_byteified
from crawl import crawlModule
import requests
from bs4 import BeautifulSoup
from data_diff import Diff
import codecs
import json
import soupsieve
import bs4
import backports.functools_lru_cache
import os
import sys
import io
import re
import uuid
import shutil


bspath = os.path.join(os.path.dirname(os.path.abspath(
    __file__)), "libraries/backports.functools_lru_cache-1.6.1")
sys.path.append(bspath)
bspath = os.path.join(os.path.dirname(os.path.abspath(
    __file__)), "libraries/beautifulsoup4-4.8.0")
sys.path.append(bspath)
bspath = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "libraries/soupsieve-1.9.5")
sys.path.append(bspath)

# DEFAULTS
DEFAULT_VERSION_PATH = 'releases/versions.json'
DEFAULT_CANDIDATE_PATH = 'candidates/'
DEFAULT_RELEASE_PATH = 'releases/'
DEFAULT_CONFIG_PATH = 'configs/'

VERSION_REGEX = re.compile("([0-9]{1,2}.){2}[0-9]{1,2}")
# pattern.match(string)


def increment_ver(version, maxVersion=50):
    if version is None or not VERSION_REGEX.match(version):
        return '0.0.1'
    version = version.split('.')
    if(int(version[2]) < 50):
        version[2] = str(int(version[2]) + 1)
    elif(int(version[1]) < 50):
        version[1] = str(int(version[1]) + 1)
        version[2] = "0"
    else:
        version[0] = str(int(version[0]) + 1)
        version[1] = "0"
        version[2] = "0"
    return '.'.join(version)

def emptyFolder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

crawlModule('configs/announcements.config.json')