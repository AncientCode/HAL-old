# Combinations and Permuations

import math

def p(n, r):
    return reduce(lambda x, y: x*y, xrange(n-r+1, n+1))

def c(n, r):
    return p(n, r) / math.factorial(r)

funcs = dict(permut=p, combo=c)
