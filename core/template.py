from sexpdata import Symbol

EPS_INDEX = 5
K_INDEX = 8
INTEGRAL_INDEX = 9

TEMPLATE = [[Symbol('set-logic'), Symbol('QF_NRA')], [Symbol('declare-fun'), Symbol('pi'), [], Symbol('Real')],
            [Symbol('assert'), [Symbol('>='), Symbol('pi'), 3.141592653589793]],
            [Symbol('assert'), [Symbol('<='), Symbol('pi'), 3.141592653589793]],
            [Symbol('declare-fun'), Symbol('eps'), [], Symbol('Real')],
            [Symbol('assert'), [Symbol('>='), Symbol('eps'), 0.1]],
            [Symbol('assert'), [Symbol('<='), Symbol('eps'), 1]],
            [Symbol('declare-fun'), Symbol('k'), [], Symbol('Real')],
            [Symbol('assert'), [Symbol('='), Symbol('k'), 10]], [Symbol('assert'), [Symbol('not'), [Symbol('<=')]]],
            [Symbol('check-sat')], [Symbol('exit')]]
