from __future__ import division
import re
import imp
import math
import uuid
import gmpy2
import os.path
import traceback
import __builtin__
from glob import glob

from HALapi import get_main_dir, module_filter, HALcannotHandle

# Some version of gmpy2 doesn't have pow()
try:
    gmpy2.pow(2, 10)
except (AttributeError, TypeError):
    gmpy2.pow = lambda x, y: x**y

gmpy2.context().precision = 256

math_list = ['acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh', 'exp', 'floor', 'fmod', 'hypot', 'modf', 'pow', 'sin', 'sinh', 'sqrt', 'tan', 'tanh']
builtin_list = ['abs']

funcs = dict((name, getattr(gmpy2, name)) for name in math_list)
funcs.update(dict((name, getattr(__builtin__, name)) for name in builtin_list))
funcs.update(fact=math.factorial, mpfr=gmpy2.mpfr, arctan=gmpy2.atan, arccos=gmpy2.acos, arcsin=gmpy2.asin, log=gmpy2.log10,
             ln=gmpy2.log)
const = dict(e =gmpy2.mpfr('2.7182818284590452353602874713526624977572470936999595749669676277240766303535475945713821785251664274'),
             pi=gmpy2.mpfr('3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679'))
filters = {
    '^': '**',
    re.compile(r'([0-9]+)!'): lambda m: 'fact(%s)'%m.group(1),
}

#requation = re.compile(r'[+0-9-*/.!^ ()]{3,}')
#refuncs = '|'.join(funcs)
#requation = re.compile(r'(?:[0-9]|(?<=[0-9)a-z])[+/\-*^](?=[0-9(]|'+refuncs+r')|(?<=[0-9])!|[()]|'+refuncs+r'|(?<=[0-9\s)]),(?=[\s0-9a-z]))+')
rempfr = re.compile(r'[0-9]+(?:\.[0-9]+)?')
fmpfr = lambda m: "mpfr('%s')"%m.group(0)
renodec = re.compile(r'\.0(?=[^\d]|$)')

class HALequation(object):
    # Plugin interface
    def __init__(self, write):
        dir = os.path.join(get_main_dir(), 'plugins/math')
        files = filter(bool, map(module_filter, glob(os.path.join(dir, '*'))))
        for file in files:
            self.funcs = dict(funcs)
            if write:
                print 'Loading math extension "%s"...'%file
            try:
                data = imp.find_module(file, [dir])
                module = imp.load_module(str(uuid.uuid1()), *data)
                if hasattr(module, 'funcs') and type(module.funcs) is dict:
                    self.funcs.update(module.funcs)
            except:
                print 'Error in math extension', file
                traceback.print_exc()
        refuncs = '|'.join(self.funcs)
        self.requation = re.compile(r'(?:[0-9]|(?<=[0-9)a-z])[+/\-*^](?=[0-9(]|'+refuncs+r')|(?<=[0-9])!|[()]|(?:'+refuncs+r')(?=[(])|(?<=[0-9\s)]),(?=[\s0-9a-z])|'+'|'.join(const)+r')+')
        self.refunc = re.compile(r'(?:'+refuncs+r')\(.*\)', re.I)
        self.funcs.update(const)

    def check_bracket(self, input):
        count = 0
        for i in input:
            if i == '(':
                count += 1
            elif i == ')':
                count -= 1
            if count < 0:
                return False
        return count == 0

    def find_front_list(self, str, iter):
        for item in iter:
            if str.find(item) == 0:
                return True

    def find_back_list(self, str, iter):
        for item in iter:
            k = str.rfind(item)
            if k >= 0 and k == len(str)-len(item):
                return True

    def bracket_multiply(self, input):
        out = bytearray(' ')
        for index, i in enumerate(input):
            if i == '(':
                if chr(out[-1]) in '0123456789' or out[-1] == ')':
                    out.append('*')
            elif chr(out[-1]) in '0123456789' and self.find_front_list(input[index:], self.funcs):
                out.append('*')
            elif i in '0123456789' and self.find_back_list(str(out), self.funcs):
                out.append('*')
            out.append(i)
        return str(out[1:])

    def solve(self, equation):
        while True:
            res = self.requation.search(equation)
            if res is None:
                return False
            eq = res.group(0).strip()
            if eq:
                equation = eq
                break
            equation = equation[:res.start()] + equation[res.end():]
        if not self.check_bracket(equation):
            return False
        equation = self.bracket_multiply(equation)
        for orig, repl in filters.iteritems():
            try:
                equation = orig.sub(repl, equation)
            except AttributeError:
                equation = equation.replace(orig, repl)
        equation = rempfr.sub(fmpfr, equation)
        try:
            return eq, renodec.sub('', str(eval(equation, {'__builtins__': None}, self.funcs)))
        except:
            if hasattr(__builtin__, 'TEST_EQUATION') and __builtin__.TEST_EQUATION:
                return 'eval failed:\n'+traceback.format_exc()
            else:
                return False

    def check(self, input):
        if self.refunc.search(input) is not None:
            return True
        operators = '/*-+%^'
        numbers = '0123456789'
        space = ' \t\r\n\f\a'
        brackets = '()[]{}'
        
        input = self.bracket_multiply(input)
        
        state = ''
        bracket = False
        found = False
        for index, i in enumerate(input):
            if i in numbers or self.find_front_list(input[index:], const):
                if not state:
                    state = 'n'
                elif state == 'no':
                    found = True
                    break
            elif i in operators:
                if state == 'n':
                    state = 'no'
                else:
                    state = ''
            elif i in space:
                pass
            elif i in brackets:
                bracket = True
            else:
                state = ''
        
        if found and bracket:
            return check_bracket(input)
        return found
    
    def answer(self, input):
        data = self.solve(input)
        if data is False:
            raise HALcannotHandle
        elif type(data) is str:
            return data
        equation, answer = data
        return (equation if len(equation) < 30 else 'That') + ' equals to ' + answer + '.'

if __name__ == '__main__':
    __builtin__.TEST_EQUATION = True
    eq = HALequation(True)
    while True:
        print eq.answer(raw_input('>>> '))
