try:
    from HALnative import solve_equation, generate_equation
except ImportError:
    from HALnative import (solveEquation as solve_equation,
                           generateEquation as generate_equation)

try:
    #from HALnative import check_bracket, bracket_multiply
    raise ImportError # Comment this line and uncomment the previous to use c++
except ImportError:
    def check_bracket(input):
        count = 0
        for i in input:
            if i == '(':
                count += 1
            elif i == ')':
                count -= 1
            if count < 0:
                return False
        return count == 0
    def bracket_multiply(input):
        out = ' '
        for i in input:
            if i == '(':
                if out[-1] in '0123456789' or out[-1] == ')':
                    out += '*'
            out += i
        return out[1:]

def check(input):
    operators = '/*-+%^'
    numbers = '0123456789'
    space = ' \t\r\n\f\a'
    brackets = '()[]{}'
    
    input = bracket_multiply(input)
    
    state = ''
    bracket = False
    found = False
    for i in input:
        if i in numbers:
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

def answer(input):
    equation = generate_equation(input)
    return (equation if len(equation) < 30 else 'That') + ' equals to ' + solve_equation(equation, 4) + '.'
