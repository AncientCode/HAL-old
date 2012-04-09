from getpass import getuser
import random
import os.path
import re
import difflib

from HALformat import check_blank, check_for_end, sentence_split
from HALnative import HALBot
import equation
from HALwiki import HALwiki
from HALapi import HALcannotHandle
from HALmacro import HALmacro
#import language
import HALspeak

try:
    _user = getuser()
except:
    _user = None


# TODO: Combine multiple matches into one
# i.e. 2 #HELLO sections will be combined into in pick_match()
class HALintel(HALBot):
    junks = '!@#$%^()_~`./\\?,'
    regroups = re.compile(r'\\g<([1-9][0-9]*?)>')
    def __init__(self, path, *args, **kwargs):
        HALBot.__init__(self, path, *args, **kwargs)
        self.wiki = HALwiki(os.path.join(os.path.split(path)[0], 'clean.chal'))
    def check(self, input):
        return True
    def pick_match(self, ques, array):
        diff = difflib.SequenceMatcher(a=ques.upper(), isjunk=lambda x: x in self.junks)
        sorted = []
        for possible in array:
            diff.set_seq2(possible[0].replace('\\', ''))
            match = diff.ratio()
            sorted.append((match,) + possible)
        best = max(sorted, key=lambda a: a[0])
        return best
    def pick_ans(self, ques, best):
        match, pattern, thinkset, answers, groups = best
        answers = [i.replace('^', r'\g<1>').replace('*', r'\g<1>') for i in answers]
        groups = [i.strip() for i in groups]
        filtered = []
        for answer in answers:
            ids = [int(i) for i in self.regroups.findall(answer)]
            is_ok = True
            for id in ids:
                if not (id < len(groups) and groups[id]):
                    is_ok = False
                    break
            if not is_ok:
                continue
            filtered.append(answer)
        answers = filtered
        if not answers:
            raise HALcannotHandle
        answer = random.choice(answers)
        return thinkset, answer, groups
    def subst_groups(self, ans, groups):
        #func = lambda a: groups[int(a.group(1))]
        #print (ans, groups)
        return self.regroups.sub(lambda a: groups[int(a.group(1))], ans)
        #return re.sub(r'\g<([1-9][0-9]*?)>', lambda a: groups[int(a.group(1))], ans)
    def answer(self, question):
        best, other = self.Ask(question)
        #print question, best, other
        if best:
            ans = self.pick_match(question, best)
            if ans[0] < 0.3:
                other.append(ans[1:])
            else:
                other = []
        if other:
            ans = self.pick_match(question, other)
        try:
            if not ans:
                raise HALcannotHandle
        except NameError:
            # ans not defined
            raise HALcannotHandle
        thinkset, answer, groups = self.pick_ans(question, ans)
        answer = self.subst_groups(answer, groups)
        if answer[0] == '>':
            return self.answer(answer[1:])
        if '$HALWIKI$' in answer:
            return self.wiki.getwiki(question)
        return answer

class HAL(object):
    version = '0.018'
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
            self.generic.append("I can't seem to understand.")
        except IOError:
            self.generic = ["I have a problem with my brain, I can't think..."]
        self.macro = HALmacro(username)
        self.speak = speak
        self.sphandle = None
        self.speak_opt = dict(volume=100, speed=175, gender=True, lang='en-us')
        self.data_folder = path
        self.debug_write = write
        
        self._init_readable()
        self._init_remove()
    
    def _init_readable(self):
        self.readable = {}
        readable_subst_path = os.path.join(self.data_folder, 'readable.chal')
        if self.debug_write:
            print 'Reading', readable_subst_path, 'for computer readable substitution...'
        try:
            file = open(readable_subst_path)
        except IOError:
            print 'Failed to read', readable_subst_path, 'for Computer Readable Substitition!!!'
        else:
            for line in file:
                fields = line.strip('\n').split('\t')
                regex = re.compile(re.escape(fields[0]), re.IGNORECASE)
                self.readable[regex] = fields[1]
    
    def _init_remove(self):
        self.remove = []
        word_removal_path = os.path.join(self.data_folder, 'remove.chal')
        if self.debug_write:
            print 'Reading', word_removal_path, 'for word removal...'
        try:
            file = open(word_removal_path)
        except IOError:
            print 'Failed to read', word_removal_path, 'for word removal!!!'
        else:
            for line in file:
                regex = re.compile(r'\b'+re.escape(line.strip()+r'\b'), re.IGNORECASE)
                self.remove.append(regex)
    
    def _clean_text(self, text):
        for regex, replacement in self.readable.iteritems():
            text = regex.sub(replacement, text)
        for regex in self.remove:
            text = regex.sub('', text)
        return text
    
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
        
        question = self._clean_text(question)
        
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
            self.sphandle = HALspeak.speak(' '.join(answers), False, **self.speak_opt)
        return answers
        #if is_foreign:
        #    return [language.translate(i, 'en', lang) for i in answers]
        #else:
        #    return answers
