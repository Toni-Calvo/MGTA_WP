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
    
    A = np.zeros((len(fpDic), nFlight*len(fpDic)))
    
    for i in range(len(A)):
        for j in range(len(A[0])):
            if (j - i) % len(fpDic) == 0:
                A[i][j] = 1
    
    b = np.ones((1, len(fpDic)))
    
    Aeq = np.zeros((nFlight, nFlight*len(fpDic)))
    
    for i in range(len(Aeq)):
        for j in range(len(Aeq[0])):
            if 0 <= j - i*len(fpDic) < len(fpDic):
                Aeq[i][j] = 1
            else:
                Aeq[i][j] = 0
                
    beq = np.ones((1, nFlight))
    
    bounds = [(0, 1)] * nFlight*len(fpDic)
    res = sp.optimize.linprog(c, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq, bounds=bounds)
    
    for index in range(len(res.x)): #! Si que hay unos comprobar con sistema mas sencillo
        if res.x[index] == 1:
            print(index)
        
    print(res.x)
    
            
    

def getFilteredSlots(fpDic):
    """Returns a vector with all the slots."""
    slots = []
    for key in fpDic:
        slots.append(int(key.split(':')[0])*60 + int(key.split(':')[1]))
    
            
    
    
def setCostFunc(fpDic, rf):
    """Returns the cost of the delay."""
    pass
    
# --------------------------------------------------------------------------------------------
# MAIN PROGRAM

arrivals, HnoReg = main()
fpDic = assignSlots(arrivals, getSlots(AAR, PAAR, rStart, rEnd))
fpDic = filterFPs(fpDic, rStart, HnoReg)
buildMatrix(fpDic)
print()