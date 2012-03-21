from getpass import getuser

from HALformat import check_blank, check_for_end, sentence_split
from HALnative import HALBot
import HALdatetime
import equation
import HALwiki
from HALapi import HALcannotHandle

try:
    _user = getuser()
except:
    _user = None

class HAL(object):
    version = '0.011'
    handlers = [equation, HALdatetime, HALwiki]
    def __init__(self, username=None, path='data', write=False):
        if username is None:
            if _user is None:
                self.user = raw_input('Enter a username: ')
            else:
                self.user = _user
        else:
            self.user = username
        self.intel = HALBot(path, self.user, write)
        self.running = True
    
    def shutdown(self):
        return 'Goodbye, %s. I enjoyed talking to you.'%self.user
    
    def ask(self, question):
        answers = []
        
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
                # Let C++ handle it
                answers.append(self.intel.Ask(sentence))
        return answers
