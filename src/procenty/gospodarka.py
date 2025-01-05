import numpy as np
from scipy.optimize import fsolve


k = 1.8
beta = 1000
M = 300
Pc = 2

alfa = 0.5
omega = 0.5
A = 1000

def rownaniestanu(vars):

    Y, r = vars
    eq1 = r - (k/beta)*Y + (1/beta)*(M/Pc)
    eq2 = r + (1/(alfa*omega))*Y - A/omega
    return [eq1, eq2]


def oblicz():
    Y_eq, r_eq = fsolve(rownaniestanu, [3, 5])

    return Y_eq, r_eq

for i in range(1, 10):
    Pc = i
    print(oblicz())