import scipy as sp
import numpy as np
from wp1 import main, isInECAC, getDistance, getSlots, plotSlotsArrOverTime, assignSlots, getCategory
from wp2 import getAirConsumption, getGroundConsumption

# --------------------------------------------------------------------------------------------
# GLOBAL VARIABLES
Hfile = 6
AAR = 38
PAAR = 12
rStart = 8
rEnd = 13
rf = 1 # €/min
epsilon = 0
fuel_cost = 704.5 #$/t price of one ton of jet fuel at 15th of November
fuel_cost = fuel_cost*0.948/1000 # €/kg


# --------------------------------------------------------------------------------------------
# FUNCTIONS

def filterFPs(fpDic, Hstart, HnoReg):
    """Filters all the flightplans to only show the ones between Hstart and HnoReg."""
    filteredFPs = {}
    for key in fpDic:
        if Hstart * 60 <= (int(key.split(':')[0]) * 60 + int(key.split(':')[1])) <= (HnoReg[0] * 60 + HnoReg[1]):
            newKey = int(key.split(':')[0]) * 60 + int(key.split(':')[1]) - Hstart * 60
            newKey = str(newKey // 60) + ':' + str(newKey % 60)
            filteredFPs.update({newKey : fpDic.get(key)})
    
    for key in filteredFPs:
        if filteredFPs.get(key) != None:
            arrival = filteredFPs.get(key).get('aHour') * 60 + filteredFPs.get(key).get('aMin') - Hstart*60
            departure = filteredFPs.get(key).get('dHour') * 60 + filteredFPs.get(key).get('dMin') - Hstart*60
            filteredFPs.get(key).update({'aHour' : arrival // 60})
            filteredFPs.get(key).update({'aMin' : arrival % 60})
            filteredFPs.get(key).update({'dHour' : departure // 60})
            filteredFPs.get(key).update({'dMin' : departure % 60})
            
    return filteredFPs


def buildMatrix(fpDic):
    """Builds the slot/flights matrix."""
    nFlight = 0
    for key in fpDic:
        if fpDic.get(key) != None:
            nFlight += 1
            
    c = np.ones((1, nFlight*len(fpDic))) # filas: vuelos, columnas: slots
    keys = list(fpDic.keys())
    
    for i in range(len(c[0])):
        index = i % len(fpDic)
        
        if fpDic.get(keys[index]) == None:
            c[0][i] = 1e9
            continue
        
        et = fpDic.get(keys[index]).get('aHour') * 60 + fpDic.get(keys[index]).get('aMin')
        if index == len(keys) - 1:
            t = int(keys[index].split(':')[0]) * 60 + int(keys[index].split(':')[1]) + PAAR
        else:
            t = int(keys[index + 1].split(':')[0]) * 60 + int(keys[index + 1].split(':')[1])
            
        if t < et:
            c[0][i] = 1e9
        else:
            c[0][i] = getRF(fpDic.get(keys[index]).get('aircraft_type'),t - et) * (t - et)**(1 + epsilon)
            """if t - et <= 5:
                c[0][i] = rf * (t - et)**(1 + epsilon)
            elif t - et <= 15:
                c[0][i] = (5 * rf + rf * (t - et - 5))**(1 + epsilon) #! Cambiar rf por el cost0005/cost0515
            elif t - et <= 30:
                c[0][i] = (5 * rf + 10 * rf + rf * (t - et - 15))**(1 + epsilon)
            else:
                c[0][i] = (5 * rf + 10 * rf + 15 * rf + rf * (t - et - 30))**(1 + epsilon)"""
    
    A = np.zeros((len(fpDic), nFlight*len(fpDic)))
    
    for i in range(len(A)): # Cada slot solo tiene un vuelo
        for j in range(len(A[0])):
            if (j - i) % len(fpDic) == 0:
                A[i][j] = 1
    
    b = np.ones((1, len(fpDic)))
    
    Aeq = np.zeros((nFlight, nFlight*len(fpDic)))
    
    for i in range(len(Aeq)):   # Cada vuelo solo tiene un slot
        for j in range(len(Aeq[0])):
            if 0 <= j - i*len(fpDic) < len(fpDic):
                Aeq[i][j] = 1
            else:
                Aeq[i][j] = 0
                
    beq = np.ones((1, nFlight))
    
    bounds = [(0, 1)] * nFlight*len(fpDic)
    res = sp.optimize.linprog(c, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq, bounds=bounds)
    
    delay = 0
    for index in range(len(res.x)): #! Si que hay unos comprobar con sistema mas sencillo
        if res.x[index] == 1:
            print(index)
            delay += (c[0][index]/rf)**(1/(1 + epsilon))
        
    print(delay)
    
    
def getRF(aircraft, delay):
    """Returns the cost of the delay."""
    if cost.get(aircraft) is None:
        aircraft = getCategory(aircraft=aircraft)
    if delay <= 5:
        return cost[aircraft].get('cost_gd_0005')
    elif delay <= 15:
        return cost[aircraft].get('cost_gd_0515')
    elif delay <= 30:
        return cost[aircraft].get('cost_gd_1530')
    else:
        return cost[aircraft].get('cost_gd_3060')
    
    
def getFilteredSlots(fpDic):
    """Returns a vector with all the slots."""
    slots = []
    for key in fpDic:
        slots.append(int(key.split(':')[0])*60 + int(key.split(':')[1]))
    


def cost_file(filepath):
    cost_data = {}  # List to hold all cost data
    #filepath += '.txt'
    with open(filepath, 'r') as file:
        for line in file:
            cAircraft = line.rstrip().replace(",", "").split('\t' + 'â‚¬')
            # Slopes of each section of the delay
            slope0515 = round(int(cAircraft[1])/5, 2)
            slope1530 = round((int(cAircraft[2])-int(cAircraft[1]))/10, 2)
            slope3060 = round((int(cAircraft[3])-int(cAircraft[2]))/15, 2)
            cost_dict = {
                'cost_gd_0005': round(getGroundConsumption(cAircraft[0]) * fuel_cost/60, 2),
                'cost_gd_0515': slope0515,
                'cost_gd_1530': slope1530,
                'cost_gd_3060': slope3060,
                'cost_ad_0005': round(getAirConsumption(cAircraft[0]) * fuel_cost/60, 2),
                'cost_ad_0515': round(int(cAircraft[7])/5, 2),
                'cost_ad_1530': round((int(cAircraft[8])-int(cAircraft[7]))/10, 2),
                'cost_ad_3060': round((int(cAircraft[9])-int(cAircraft[8]))/15, 2),
            }
            cost_data.update({cAircraft[0] : cost_dict})

    cost_data = computeAvrgForCategory(cost_data)
    return cost_data


def computeAvrgForCategory(cost):
    """Computes the average cost for each category."""
    escalado = 1.2
    b = 0
    tb = [0] * 8
    c = 0
    tc = [0] * 8
    d = 0
    td = [0] * 8
    e = 0
    te = [0] * 8
    f = 0
    tf = [0] * 8
    
    for aircraft in cost:
        category = getCategory(aircraft=aircraft)
        aircraft = cost.get(aircraft)
        if category == 'B':
            b += 1
            tb[0] += aircraft.get('cost_gd_0005')
            tb[1] += aircraft.get('cost_gd_0515')
            tb[2] += aircraft.get('cost_gd_1530')
            tb[3] += aircraft.get('cost_gd_3060')
            tb[4] += aircraft.get('cost_ad_0005')
            tb[5] += aircraft.get('cost_ad_0515')
            tb[6] += aircraft.get('cost_ad_1530')
            tb[7] += aircraft.get('cost_ad_3060')
        elif category == 'C':
            c += 1
            tc[0] += aircraft.get('cost_gd_0005')
            tc[1] += aircraft.get('cost_gd_0515')
            tc[2] += aircraft.get('cost_gd_1530')
            tc[3] += aircraft.get('cost_gd_3060')
            tc[4] += aircraft.get('cost_ad_0005')
            tc[5] += aircraft.get('cost_ad_0515')
            tc[6] += aircraft.get('cost_ad_1530')
            tc[7] += aircraft.get('cost_ad_3060')
        elif category == 'D':
            d += 1
            td[0] += aircraft.get('cost_gd_0005')
            td[1] += aircraft.get('cost_gd_0515')
            td[2] += aircraft.get('cost_gd_1530')
            td[3] += aircraft.get('cost_gd_3060')
            td[4] += aircraft.get('cost_ad_0005')
            td[5] += aircraft.get('cost_ad_0515')
            td[6] += aircraft.get('cost_ad_1530')
            td[7] += aircraft.get('cost_ad_3060')
        elif category == 'E':
            e += 1
            te[0] += aircraft.get('cost_gd_0005')
            te[1] += aircraft.get('cost_gd_0515')
            te[2] += aircraft.get('cost_gd_1530')
            te[3] += aircraft.get('cost_gd_3060')
            te[4] += aircraft.get('cost_ad_0005')
            te[5] += aircraft.get('cost_ad_0515')
            te[6] += aircraft.get('cost_ad_1530')
            te[7] += aircraft.get('cost_ad_3060')
        elif category == 'F':
            f += 1
            tf[0] += aircraft.get('cost_gd_0005')
            tf[1] += aircraft.get('cost_gd_0515')
            tf[2] += aircraft.get('cost_gd_1530')
            tf[3] += aircraft.get('cost_gd_3060')
            tf[4] += aircraft.get('cost_ad_0005')
            tf[5] += aircraft.get('cost_ad_0515')
            tf[6] += aircraft.get('cost_ad_1530')
            tf[7] += aircraft.get('cost_ad_3060')
    
    cost.update({'A' : {'cost_gd_0005' : round(tb[0]/b, 2) * escalado, 'cost_gd_0515' : round(tb[1]/b, 2) * escalado, 'cost_gd_1530' : round(tb[2]/b, 2) * escalado, 'cost_gd_3060' : round(tb[3]/b, 2) * escalado, 'cost_ad_0005' : round(tb[4]/b, 2) * escalado, 'cost_ad_0515' : round(tb[5]/b, 2) * escalado, 'cost_ad_1530' : round(tb[6]/b, 2) * escalado, 'cost_ad_3060' : round(tb[7]/b, 2) * escalado}})
    cost.update({'B' : {'cost_gd_0005' : round(tb[0]/b, 2), 'cost_gd_0515' : round(tb[1]/b, 2), 'cost_gd_1530' : round(tb[2]/b, 2), 'cost_gd_3060' : round(tb[3]/b, 2), 'cost_ad_0005' : round(tb[4]/b, 2), 'cost_ad_0515' : round(tb[5]/b, 2), 'cost_ad_1530' : round(tb[6]/b, 2), 'cost_ad_3060' : round(tb[7]/b, 2)}})
    cost.update({'C' : {'cost_gd_0005' : round(tc[0]/c, 2), 'cost_gd_0515' : round(tc[1]/c, 2), 'cost_gd_1530' : round(tc[2]/c, 2), 'cost_gd_3060' : round(tc[3]/c, 2), 'cost_ad_0005' : round(tc[4]/c, 2), 'cost_ad_0515' : round(tc[5]/c, 2), 'cost_ad_1530' : round(tc[6]/c, 2), 'cost_ad_3060' : round(tc[7]/c, 2)}})
    cost.update({'D' : {'cost_gd_0005' : round(td[0]/d, 2), 'cost_gd_0515' : round(td[1]/d, 2), 'cost_gd_1530' : round(td[2]/d, 2), 'cost_gd_3060' : round(td[3]/d, 2), 'cost_ad_0005' : round(td[4]/d, 2), 'cost_ad_0515' : round(td[5]/d, 2), 'cost_ad_1530' : round(td[6]/d, 2), 'cost_ad_3060' : round(td[7]/d, 2)}})
    cost.update({'E' : {'cost_gd_0005' : round(te[0]/e, 2), 'cost_gd_0515' : round(te[1]/e, 2), 'cost_gd_1530' : round(te[2]/e, 2), 'cost_gd_3060' : round(te[3]/e, 2), 'cost_ad_0005' : round(te[4]/e, 2), 'cost_ad_0515' : round(te[5]/e, 2), 'cost_ad_1530' : round(te[6]/e, 2), 'cost_ad_3060' : round(te[7]/e, 2)}})
    cost.update({'F' : {'cost_gd_0005' : round(tf[0]/f, 2), 'cost_gd_0515' : round(tf[1]/f, 2), 'cost_gd_1530' : round(tf[2]/f, 2), 'cost_gd_3060' : round(tf[3]/f, 2), 'cost_ad_0005' : round(tf[4]/f, 2), 'cost_ad_0515' : round(tf[5]/f, 2), 'cost_ad_1530' : round(tf[6]/f, 2), 'cost_ad_3060' : round(tf[7]/f, 2)}})
    
    return cost
        
# --------------------------------------------------------------------------------------------
# MAIN PROGRAM

arrivals, HnoReg = main()
fpDic = assignSlots(arrivals, getSlots(AAR, PAAR, rStart, rEnd))
fpDic = filterFPs(fpDic, rStart, HnoReg)
cost = cost_file("cost.ALL_FT+")
buildMatrix(fpDic)
print()