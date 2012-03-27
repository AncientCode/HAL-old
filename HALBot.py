from getpass import getuser

from HALformat import check_blank, check_for_end, sentence_split
from HALnative import HALBot
import equation
from HALwiki import HALwiki
from HALapi import HALcannotHandle
from HALmacro import HALmacro
import random
import os.path
#import language
import HALspeak

try:
    _user = getuser()
except:
    _user = None

class HALintel(HALBot):
    def __init__(self, path, *args, **kwargs):
        HALBot.__init__(self, path, *args, **kwargs)
        self.wiki = HALwiki(os.path.join(os.path.split(path)[0], 'clean.chal'))
    def check(self, input):
        return True
    def answer(self, question):
        res = self.Ask(question)
        if res == '$RAISE_HALCANNOTHANDLE$':
            raise HALcannotHandle
        elif '$HALWIKI$' in res:
            return self.wiki.getwiki(question)
        else:
            return res

class HAL(object):
    version = '0.014'
    def __init__(self, username=None, path='data', write=False, speak=False):
        if username is None:
            if _user is None:
                self.user = raw_input('Enter a username: ')
            else:
                self.user = _user
        else:
            self.user = username
        self.running = True
        self.handlers = [equation, HALintel(path, self.user, write)]
        try:
            with open(os.path.join(path, 'generic.chal')) as fp:
                self.generic = [i.strip() for i in fp.readlines() if i.strip() and i[0] != '#']
        except IOError:
            self.generic = ["I have a problem with my brain, I can't think..."]
        self.generic.append("I can't seem to understand.")
        self.macro = HALmacro(username)
        self.speak = speak
        self.sphandle = None
    
    def shutdown(self):
        return 'Goodbye, %s. I enjoyed talking to you.'%self.user
    
    def ask(self, question):
        answers = []
        
        #lang = language.detect_lang(question)
        #is_foreign = lang is not None and lang != 'en'
        #if is_foreign:
        #    question = language.translate(question, lang).encode('utf-8')
        
        if question is None:
            return []
        
        check = check_blank(question)
        if check is not None:
            return [check]
        
        if check_for_end(question):
            self.running = False
            return []
        
        for sentence in sentence_split(question):
            handle = False
            for handler in self.handlers:
                if handler.check(sentence):
                    try:
                        ans = handler.answer(sentence)
                    except HALcannotHandle:
                        continue
                    else:
                        answers.append(ans)
                        handle = True
                        break
            if not handle:
                answers.append(random.choice(self.generic))
        #answers = [self.macro.subst(answer) for answer in answers]
        answers = [self.macro.subst(answer) for answer in answers]
        if self.speak:
            HALspeak.stop_speaking(self.sphandle)
            self.sphandle = HALspeak.speak(' '.join(answers), False)
        return answers
        #if is_foreign:
        #    return [language.translate(i, 'en', lang) for i in answers]
        #else:
        #    return answers
