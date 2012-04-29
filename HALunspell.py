import os.path
import hunspell

import HALapi

all = ['check', 'suggest', 'analyze', 'stem', 'filter_words', 'check_all',
       'check_all', 'suggest_all', 'suggest_list']

__plugin_dir = HALapi.datadir
__hobj = hunspell.HunSpell(os.path.join(__plugin_dir, 'en_US.dic'), os.path.join(__plugin_dir, 'en_US.aff'))
__proper_letters = 'abcdefghijklmnopqrstuvwxyz '

def check(word):
    return __hobj.spell(word)

def suggest(word):
    return __hobj.suggest(word)

def analyze(word):
    return __hobj.analyze(word)

def stem(word):
    return __hobj.stem(word)

def filter_words(text):
    letters = []
    for letter in text.lower():
        if letter in __proper_letters:
            letters.append(letter)
    return ''.join(letters)

def check_all(text):
    words = filter_words(text).split()
    return len(words), words, check_list(words)

def check_list(words):
    return map(__hobj.spell, words)

def suggest_all(text):
    words = filter_words(text).split()
    return len(words), words, suggest_list(words)

def suggest_list(words):
    return map(__hobj.suggest, words)
