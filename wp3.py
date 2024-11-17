import scipy as sp
import numpy as np
from wp1 import main, isInECAC, getDistance, getSlots, plotSlotsArrOverTime, assignSlots

# --------------------------------------------------------------------------------------------
# GLOBAL VARIABLES
Hfile = 6
AAR = 38
PAAR = 12
rStart = 8
rEnd = 13
rf = 1 # €/min
epsilon = 0

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
            c[0][i] = rf * (t - et)**(1 + epsilon)
    
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
    
            
    
def getFilteredSlots(fpDic):
    """Returns a vector with all the slots."""
    slots = []
    for key in fpDic:
        slots.append(int(key.split(':')[0])*60 + int(key.split(':')[1]))
    
            
    
    
def setCostFunc(fpDic, rf):
    """Returns the cost of the delay."""
    pass

def cost_file(filepath):
    cost_data = []  # List to hold all cost data
    with open(filepath, 'r') as file:
        for line in file:
            cAircraft = line.strip().split('\t')
            # Slopes of each section of the delay
            slope0005 = 1 #Mirar coste fuel
            slope0515 = int(cAircraft[1]/5)
            slope1530 = int(cAircraft[2]-cAircraft[1]/10)
            slope3060 = int(cAircraft[3]-cAircraft[2]/15)
            cost_dict = {
                'aircraft_type': cAircraft[0],
                'cost_gd_0005': slope0005,
                'cost_gd_0515': slope0515,
                'cost_gd_1530': slope1530,
                'cost_gd_3060': slope3060,
                'cost_ad_0005': 1, #Mirar coste fuel
                'cost_ad_0515': int(cAircraft[7]/5),
                'cost_ad_1530': int(cAircraft[8]-cAircraft[7]/10),
                'cost_ad_3060': int(cAircraft[9]-cAircraft[8]/15),
            }
            cost_data.append(cost_dict)
            print(list[0].get('cost_gd_0005'))

    return cost_data    
# --------------------------------------------------------------------------------------------
# MAIN PROGRAM

arrivals, HnoReg = main()
fpDic = assignSlots(arrivals, getSlots(AAR, PAAR, rStart, rEnd))
fpDic = filterFPs(fpDic, rStart, HnoReg)
buildMatrix(fpDic)
list = cost_file("cost")
print(list[0].get('cost_gd_0005'))
print()