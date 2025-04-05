from scipy import optimize 
from dataclasses import dataclass
import datetime as dt
from dateutil.relativedelta import relativedelta




def npv(rate, cash_flows):
    return sum([cf / (1 + rate) ** i for i, cf in enumerate(cash_flows)])


def irr(cash_flows):
    rate = 0.1
    while npv(rate, cash_flows) > 0:
        rate += 0.01
    return rate




def secant_method(tol, f, x0):
    """
    Solve for x where f(x)=0, given starting x0 and tolerance.
    
    Arguments
    ----------
    tol: tolerance as percentage of final result. If two subsequent x values are with tol percent, the function will return.
    f: a function of a single variable
    x0: a starting value of x to begin the solver

    Notes
    ------
    The secant method for finding the zero value of a function uses the following formula to find subsequent values of x. 
    
    x(n+1) = x(n) - f(x(n))*(x(n)-x(n-1))/(f(x(n))-f(x(n-1)))
    
    Warning 
    --------
    This implementation is simple and does not handle cases where there is no solution. Users requiring a more robust version should use scipy package optimize.newton.

    """

    x1 = x0*1.1
    while (abs(x1-x0)/abs(x1) > tol):
        x0, x1 = x1, x1-f(x1)*(x1-x0)/(f(x1)-f(x0))
    return x1

def xnpv(rate,cashflows):
    """
    Calculate the net present value of a series of cashflows at irregular intervals.

    Arguments
    ---------
    * rate: the discount rate to be applied to the cash flows
    * cashflows: a list object in which each element is a tuple of the form (date, amount), where date is a python datetime.date object and amount is an integer or floating point number. Cash outflows (investments) are represented with negative amounts, and cash inflows (returns) are positive amounts.
    
    Returns
    -------
    * returns a single value which is the NPV of the given cash flows.

    Notes
    ---------------
    * The Net Present Value is the sum of each of cash flows discounted back to the date of the first cash flow. The discounted value of a given cash flow is A/(1+r)**(t-t0), where A is the amount, r is the discout rate, and (t-t0) is the time in years from the date of the first cash flow in the series (t0) to the date of the cash flow being added to the sum (t).  
    * This function is equivalent to the Microsoft Excel function of the same name. 

    """

    chron_order = sorted(cashflows, key = lambda x: x[0])
    t0 = chron_order[0][0] #t0 is the date of the first cash flow

    return sum([cf/(1+rate)**((t-t0).days/365.0) for (t,cf) in chron_order])

def xirr(cashflows,guess=0.1):
    """
    Calculate the Internal Rate of Return of a series of cashflows at irregular intervals.

    Arguments
    ---------
    * cashflows: a list object in which each element is a tuple of the form (date, amount), where date is a python datetime.date object and amount is an integer or floating point number. Cash outflows (investments) are represented with negative amounts, and cash inflows (returns) are positive amounts.
    * guess (optional, default = 0.1): a guess at the solution to be used as a starting point for the numerical solution. 

    Returns
    --------
    * Returns the IRR as a single value
    
    Notes
    ----------------
    * The Internal Rate of Return (IRR) is the discount rate at which the Net Present Value (NPV) of a series of cash flows is equal to zero. The NPV of the series of cash flows is determined using the xnpv function in this module. The discount rate at which NPV equals zero is found using the secant method of numerical solution. 
    * This function is equivalent to the Microsoft Excel function of the same name.
    * For users that do not have the scipy module installed, there is an alternate version (commented out) that uses the secant_method function defined in the module rather than the scipy.optimize module's numerical solver. Both use the same method of calculation so there should be no difference in performance, but the secant_method function does not fail gracefully in cases where there is no solution, so the scipy.optimize.newton version is preferred.

    """
    
    #return secant_method(0.0001,lambda r: xnpv(r,cashflows),guess)
    return optimize.newton(lambda r: xnpv(r,cashflows),guess)


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
                return "N/A"

        return rrso
    

def liczba_dni_w_roku(rok):
    if rok % 4 == 0:
        dni_rok = 366
    else:
        dni_rok = 365
    
    return dni_rok

def mpkk(K, N, data_start):
    # 28.12.2020 - 04.01.2021
    # 29,30,31,1,2,3,4
    # 3 + 4 = 7


    data_koniec = data_start + relativedelta(months=N)

    # get year out of data_start
    rok_start = data_start.year
    rok_koniec = data_koniec.year

    if rok_start == rok_koniec:
        dni_rok = liczba_dni_w_roku(rok_start)
        dni = (data_koniec - data_start).days
        # print(f"ile dni {dni}")
        mpkk = K * 0.1 + K * dni/dni_rok * 0.1
    else:
        wspolczynnik = 0
        for rok in range(rok_start, rok_koniec+1):
            # sprawdz czy rok startowy jest przestepny
            if rok == rok_start:
                dni_rok = liczba_dni_w_roku(rok)
                dni = (dt.datetime(rok,12,31) - data_start).days
                wspolczynnik = dni/dni_rok
            elif rok == rok_koniec:
                dni_rok = liczba_dni_w_roku(rok)
                dni = (data_koniec - dt.datetime(rok-1,12,31)).days
                wspolczynnik += dni/dni_rok
            else:
                wspolczynnik += 1

        mpkk = K * 0.1 + K * wspolczynnik * 0.1

    return mpkk



if __name__ == "__main__":
    cf = [-1000, 300, 300, 300, 300]
    print(npv(0.1, cf))
    print(irr(cf))