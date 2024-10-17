

def npv(rate, cash_flows):
    return sum([cf / (1 + rate) ** i for i, cf in enumerate(cash_flows)])


def irr(cash_flows):
    rate = 0.1
    while npv(rate, cash_flows) > 0:
        rate += 0.01
    return rate


if __name__ == "__main__":
    cf = [-1000, 300, 300, 300, 300]
    print(npv(0.1, cf))
    print(irr(cf))