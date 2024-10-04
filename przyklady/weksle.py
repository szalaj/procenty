from procenty.podmioty import Firma, BankCentralny, Weksel

def firm():
    firma = Firma(1000, 200, 100, 5)
    print(firma.symulacja())



def symulacja(liczba_krokow=10):
    print(liczba_krokow)

    wynik = []

    # kapital poczatykowy przedsiebiorcow
    K0= 1000
    ro = 0.2
    cz = 2
    cw = 1
    rm = 0.1
    rk = 0.2
    rd = 0.1
    k=1
    N = 60
    cn = 1



    for g in range(4):
        # P0 = W0*(cz-cw)
        # K = b.D*(1-b.rr)
        W0 = K0/cw

        Z0 = k*W0
        Placa = W0*cw

        Zh0 = Placa/cz

        Zd = Z0 - Zh0

        P0 = Zh0*cz - Placa

        # S0 = Placa*(rk/(1+rk))       

        Pi = P0
        # S = S0
        # G = G0
        
        # Pb = 0
   
        Pis = [P0]
        # Sis = [0]
        # Gis = [G0]
        # Pbis = [0]
        # Placas = [Placa]
        M = [P0 + Placa]


        # print(M)
        for i in range(1,liczba_krokow):


            Ki = Pis[i-1]
            Wi = Ki/cw
            Zi = k*Wi
            Zhi = Wi*cw/cz
            Zd += (Zi - Zhi)
            Pi = Zhi*cz - Wi*cw
            Placa = Wi*cw
            Mi = Pi + Placa + Zd*cz


            # print(i)
            # Si = Placas[i-1]*(rk/(1+rk))
            # Gi = Placas[i-1] - Si

            # S = S + Si
            # G = G + Gi

            # Li = S*(1-ro)
            # Ki = Pi + Li
            # Wi = Ki/cw

            # Pi = k*Wi*cz - Wi*cw - Li*rk
            # Pbi = Li*(rk-rd)
            # Pb = Pb + Pbi
            # Placas.append(Wi*cw + S*rd - N*cn)

            # Mi = S+G+Pb+Pi

            # M_d =  Mi - M[i-1] 

            # # print(M_d - k*Wi*cz - Pbi)

            # if Zd < 0:
            #     cz += 0.1
            # else:
            #     cz -= 0.8

            M.append(Mi)
            Pis.append(Pi)

            
        wynik.append({'P': Pis, 'M':M})

    return wynik


if __name__ == '__main__':
    # print(symulacja(10))
    b = BankCentralny(0.1, [])
    for i in range(100):
        weksel = Weksel(0.1, 1000, 10, i)
        b.weksle.append(weksel)

    print(b.weksle)
