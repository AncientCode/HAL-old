from getpass import getuser

from HALformat import check_blank, check_for_end, sentence_split
from HALnative import HALBot
from HALdatetime import is_datetime, answer_datetime
import equation

try:
    _user = getuser()
except:
    _user = None

class HAL(object):
    version = '0.011'
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
            if equation.check(sentence):
                answers.append(equation.answer(sentence))
            elif is_datetime(sentence):
                answers.append(answer_datetime(sentence))
            else:
                # Let C++ handle it
                answers.append(self.intel.Ask(sentence))
        return answers

        