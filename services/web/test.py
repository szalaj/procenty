import utils.rrso as rs

K = 460000
N = 360
p = 0.0323

R = rs.oblicz_rate(K,12,N,p)

print(R)

raty = [{'rata':R} for i in range(N)]

rrso = rs.RRSO(K, raty, p)

i2 = rrso.oblicz_rrso2()

r = rrso.oblicz_rrso()

r2 = (1+i2)**12-1

print(f'rrso: {i2}, rrso2: {r2}, rrso: {round(100*r,2)}')


R_t = rs.oblicz_rate(1000,2,4,0.12)
print(R_t)

x = lambda x: R_t*(1+x)**-0.5 + R_t*(1+x)**-1 + R_t*(1+x)**-1.5 + R_t*(1+x)**-2

print(round(x(0.1236),2))