import re
import enchant
import os.path
import __builtin__

class SpamDetect:
    vowels = 'aeiouy'
    consonants = 'bcdfghjklmnpqrstvwxz'
    proper_letters = 'abcdefghijklmnopqrstuvwxyz '
    homerow = 'asdfghjkl'
    rerepeat = re.compile(r'(.)\1\1')
    rerepeatl = re.compile(r'(..+)\s*\1')

    def __init__(self, path):
        self.long_exception = [i.strip() for i in open(os.path.join(path, 'long.exc')).readlines()]
        self.impossibles = open(os.path.join(path, 'impossible.seq')).read().split()
    
    def check(self, text):
        # Strip to leave only words
        letters = []
        for letter in text.lower():
            if letter in self.proper_letters:
                letters.append(letter)
        text = ''.join(letters)
        words = text.split()

        # See if each word has a vowel, also checks length
        for word in words:
            # If word longer than 20 and not in exception list, it's spam
            if len(word) > 20 and word not in self.long_exception:
                return 'too long'
            count = 0
            for vowel in self.vowels:
                if vowel in word:
                    count += 1
            if not count:
                return 'has no vowel'
        
        # Only 3 consonant can appear in a row
        consonant = 0
        for letter in text.replace('th', 't'):
            if letter in self.consonants:
                consonant += 1
            else:
                consonant = 0
            if consonant > 3:
                return 'more than 3 consonants appear in a row'
        
        # Inavid Sequences
        for seq in self.impossibles:
            if seq in text:
                return 'invalid sequences detected'
        
        # Repitition
        for regex in (self.rerepeat, self.rerepeatl):
            if regex.search(text):
                return 'too many repeated letters'
        
        # Spell Checker
        word_count = len(words)
        count = 0
        d = enchant.Dict("en_US")
        for word in words:
            if d.check(word):
                count += 1
        error = 1-(count/word_count)
        #print count, word_count, error
        if error > 0.2:
            return 'too many non-existent words'
        
        # Passed all test, not a spam
        return False

if hasattr(__builtin__, 'IN_HAL') and __builtin__.IN_HAL:
    import random
    __plugin_dir = os.path.join(os.path.dirname(__file__), 'spam')
    __global_instance = SpamDetect(__plugin_dir)
    __answers = [i.strip() for i in open(os.path.join(__plugin_dir, 'responses.spam'))]
    def check(input):
        return __global_instance.check(input)
    def answer(input):
        return random.choice(__answers)

if __name__ == '__main__':
    detect = SpamDetect(os.path.join(os.path.dirname(__file__), 'spam'))
    while True:
        input = raw_input('>>> ')
        spam = detect.check(input)
        print repr(input), 'is spam since it has %s'%spam if spam else 'is not spam'
