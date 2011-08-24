taxrate = ((0,0.03,0),
           (1500,0.10,105),
           (4500,0.20,555),
           (9000,0.25,1055),
           (35000,0.30,2755),
           (55000,0.35,5505),
           (80000,0.45,13505))

def calcTax(pre_tax):
    taxed_salary = pre_tax - 3500
    if(taxed_salary <= 0):
        return 0
    else:
        for i in range(len(taxrate)-1,-1,-1):
            if taxed_salary > taxrate[i][0]:
                return taxed_salary*taxrate[i][1] - taxrate[i][2]


