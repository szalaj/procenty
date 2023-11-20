
from dataclasses import dataclass
import datetime as dt

@dataclass
class RRSO:
    wyplata: float
    raty: list
    rrso_0: float


    def right_side(self, rrso):

        R = 0
        for i,r in enumerate(self.raty):
            R += float(r['rata'])/((1+rrso)**((i+1)/12))
        return R
    
    def prawko(self, p):

        R = 0
        for i,r in enumerate(self.raty):
            R += float(r['rata'])/((1+p)**(i+1))
        return R
    
    def oblicz_rrso(self):
        rrso = self.rrso_0
        l_granica = 0
        r_granica = 10

        
        rs = self.right_side(rrso)

        i = 0

        while abs(self.wyplata-rs)>0.0001:
            
            if self.wyplata>rs:
                r_granica = rrso
            else:
                l_granica = rrso

            rrso = (l_granica+r_granica)/2

            
            rs = self.right_side(rrso)
            i+=1
            if i > 1000:
                raise Exception('Za dużo iteracji')

        print(f'iteracje: {i}')
        return rrso
    
    def oblicz_rrso2(self):
        rrso = self.rrso_0
        l_granica = 0
        r_granica = 5

        rs = self.prawko(rrso)

        i = 0

        while abs(self.wyplata-rs)>0.01:
            
            if self.wyplata>rs:
                r_granica = rrso
            else:
                l_granica = rrso

            rrso = (l_granica+r_granica)/2

            
            rs = self.prawko(rrso)
            i+=1
            if i > 100:
                raise Exception('Za dużo iteracji')

        print(f'iteracje: {i}')
        return rrso

def rata_rowna(kwota, okresy, i):
    rata = kwota * (i/12) / (1 - (1 + i/12)**(-okresy))
    return rata

def oblicz_rate(K,k,N,p): 



    L = (K * p)
    M = k*(1-pow(k/(k+p),N) )
    I =L/M

    return I

def sprawdz_rate(K,k,N,p,R):
    K = K
    for i in range(N):
        K -= R-K*(p/k)
    return K


