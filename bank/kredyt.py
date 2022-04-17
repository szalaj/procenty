
print('kredyt')

def bank():
    print("banki są głupie")


def rata_rowna(K, r, n, k):

    # K - Kapitał
    # r - oprocentowanie r% / 100
    # n - liczba okresow
    # k - liczba platnosci rat w roku (12)

    L = (K*r)
    M = k*(1-pow(k/(k+r),n) )

    I = L/M

    I = round(I, 2)

    return I
