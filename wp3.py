import scipy as sp
import numpy as np
from wp1 import main, getSlots, assignSlots, getCategory
from wp2 import getAirConsumption, getGroundConsumption, defineType, computePollution, getWP2Results

# --------------------------------------------------------------------------------------------
# GLOBAL VARIABLES
Hfile = 6
margin = 30 # min DO NOT CHANGE
radius = 2000 # km
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



def buildMatrix(fpDic, cost):
    """Optimizes the slot allocation."""
    fligths = []
    for key in fpDic:
        if fpDic.get(key) is not None:
            fligths.append(fpDic.get(key))
        
    slots = list(fpDic.keys())
    
    # Create the matrix
    costMatrix = np.zeros((len(fligths), len(slots)))
    for i in range(len(fligths)):
        for j in range(len(slots)):
            if j == len(slots) - 1:
                costMatrix[i][j] = getCost(fligths[i], slots[j], slots[j], cost)
            else:
                costMatrix[i][j] = getCost(fligths[i], slots[j], slots[j + 1], cost)
    
    c = costMatrix.flatten()
    bounds = [(0, 1)] * len(c)
    
    A_eq = np.zeros((len(fligths), len(c)))
    for i in range(len(fligths)):
        for j in range(len(c)):
            if j // len(slots) == i:
                A_eq[i][j] = 1
            else:
                A_eq[i][j] = 0
    
    b_eq = np.ones(len(fligths))
    
    A = np.zeros((len(slots), len(c)))
    for i in range(len(slots)):
        for j in range(len(c)):
            if j % len(slots) == i:
                A[i][j] = 1
            else:
                A[i][j] = 0
    
    b = np.ones(len(slots))

    res = sp.optimize.linprog(c, A_eq=A_eq, b_eq=b_eq, A_ub=A, b_ub=b, bounds=bounds, method='highs')
    newFP = res.x.reshape((len(fligths), len(slots)))
    newfpDic_temp = {}
    newfpDic = {}
    
    for i in range(len(fligths)):
        for j in range(len(slots)):
            if newFP[i][j] == 1:
                newfpDic_temp.update({slots[j] : fligths[i]})
    
    maxAirDelay = 0
    maxGroundDelay = 0
    maxDelaySlot = 0
    for slot in slots:
        if newfpDic_temp.get(slot) is not None:
            slotTime = int(slot.split(':')[0]) * 60 + int(slot.split(':')[1])
            newfpDic.update({slot : newfpDic_temp.get(slot)})
            if newfpDic.get(slot).get('type') == 'Regulated':
                if maxGroundDelay < slotTime - (newfpDic.get(slot).get('aHour') * 60 + newfpDic.get(slot).get('aMin')):
                    maxDelaySlot = slot
                maxGroundDelay = max(maxGroundDelay, slotTime - (newfpDic.get(slot).get('aHour') * 60 + newfpDic.get(slot).get('aMin')))
            else:
                maxAirDelay = max(maxAirDelay, slotTime - (newfpDic.get(slot).get('aHour') * 60 + newfpDic.get(slot).get('aMin')))
        else:
            newfpDic.update({slot : None})

    print(f'Total cost: {round(res.fun, 2)} €')
    print(f'Max Air Delay: {maxAirDelay} min')
    print(f'Max Ground Delay: {maxGroundDelay} min')
    print(f'Max Delay Slot: {maxDelaySlot}')
    return newfpDic
    


def getRF(flightPlan, delay, cost):
    """Returns the cost of the delay."""
    aircraft = flightPlan.get('aircraft_type')
    if cost.get(aircraft) is None:
        aircraft = getCategory(aircraft=aircraft)   # We don't have the costs of the specific flight so we take the avg of its category
        
    if flightPlan.get('type') == 'Regulated':   # Ground Delay
        if delay <= 5:
            return cost[aircraft].get('cost_gd_0005')
        elif delay <= 15:
            return cost[aircraft].get('cost_gd_0515')
        elif delay <= 30:
            return cost[aircraft].get('cost_gd_1530')
        else:
            return cost[aircraft].get('cost_gd_3060')
    else:   # Air Delay
        if delay <= 5:
            return cost[aircraft].get('cost_ad_0005')
        elif delay <= 15:
            return cost[aircraft].get('cost_ad_0515')
        elif delay <= 30:
            return cost[aircraft].get('cost_ad_1530')
        else:
            return cost[aircraft].get('cost_ad_3060')
    
    
    
def getCost(flightPlan, slot, nextSlot, cost):
    """Returns the cost of a flight plan at a certain slot."""
    slotTime = int(slot.split(':')[0]) * 60 + int(slot.split(':')[1])
    nextSlotTime = int(nextSlot.split(':')[0]) * 60 + int(nextSlot.split(':')[1])
    flightTime = flightPlan.get('aHour') * 60 + flightPlan.get('aMin')
    delay = slotTime - flightTime
    
    if flightPlan.get('type') == 'Exempt' and delay >= 20:
        return 1e12
    if delay >= 210:
        return 1e12
    if nextSlotTime - flightTime < 0:
        return 1e12
    elif delay <= 0:
        return 0
    
    return getRF(flightPlan, delay, cost) * delay**(1+epsilon)
    


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
    
    cost.update({'B' : {'cost_gd_0005' : round(tb[0]/b, 2), 'cost_gd_0515' : round(tb[1]/b, 2), 'cost_gd_1530' : round(tb[2]/b, 2), 'cost_gd_3060' : round(tb[3]/b, 2), 'cost_ad_0005' : round(tb[4]/b, 2), 'cost_ad_0515' : round(tb[5]/b, 2), 'cost_ad_1530' : round(tb[6]/b, 2), 'cost_ad_3060' : round(tb[7]/b, 2)}})
    cost.update({'C' : {'cost_gd_0005' : round(tc[0]/c, 2), 'cost_gd_0515' : round(tc[1]/c, 2), 'cost_gd_1530' : round(tc[2]/c, 2), 'cost_gd_3060' : round(tc[3]/c, 2), 'cost_ad_0005' : round(tc[4]/c, 2), 'cost_ad_0515' : round(tc[5]/c, 2), 'cost_ad_1530' : round(tc[6]/c, 2), 'cost_ad_3060' : round(tc[7]/c, 2)}})
    cost.update({'D' : {'cost_gd_0005' : round(td[0]/d, 2), 'cost_gd_0515' : round(td[1]/d, 2), 'cost_gd_1530' : round(td[2]/d, 2), 'cost_gd_3060' : round(td[3]/d, 2), 'cost_ad_0005' : round(td[4]/d, 2), 'cost_ad_0515' : round(td[5]/d, 2), 'cost_ad_1530' : round(td[6]/d, 2), 'cost_ad_3060' : round(td[7]/d, 2)}})
    cost.update({'E' : {'cost_gd_0005' : round(te[0]/e, 2), 'cost_gd_0515' : round(te[1]/e, 2), 'cost_gd_1530' : round(te[2]/e, 2), 'cost_gd_3060' : round(te[3]/e, 2), 'cost_ad_0005' : round(te[4]/e, 2), 'cost_ad_0515' : round(te[5]/e, 2), 'cost_ad_1530' : round(te[6]/e, 2), 'cost_ad_3060' : round(te[7]/e, 2)}})
    cost.update({'F' : {'cost_gd_0005' : round(tf[0]/f, 2), 'cost_gd_0515' : round(tf[1]/f, 2), 'cost_gd_1530' : round(tf[2]/f, 2), 'cost_gd_3060' : round(tf[3]/f, 2), 'cost_ad_0005' : round(tf[4]/f, 2), 'cost_ad_0515' : round(tf[5]/f, 2), 'cost_ad_1530' : round(tf[6]/f, 2), 'cost_ad_3060' : round(tf[7]/f, 2)}})
    cost.update({'A' : {'cost_gd_0005' : round((tb[0]/b) * ((tb[0]/b)/(tc[0]/c)), 2), 'cost_gd_0515' : round((tb[1]/b) * ((tb[1]/b)/(tc[1]/c)), 2), 'cost_gd_1530' : round((tb[2]/b) * ((tb[2]/b)/(tc[2]/c)), 2), 'cost_gd_3060' : round((tb[3]/b) * ((tb[3]/b)/(tc[3]/c)), 2), 'cost_ad_0005' : round((tb[4]/b) * ((tb[4]/b)/(tc[4]/c)), 2), 'cost_ad_0515' : round((tb[5]/b) * ((tb[5]/b)/(tc[5]/c)), 2), 'cost_ad_1530' : round((tb[6]/b) * ((tb[6]/b)/(tc[0]/c)), 2), 'cost_ad_3060' : round((tb[7]/b) * ((tb[7]/b)/(tc[7]/c)), 2)}})

    return cost



def setDelays(fpDic):
    """Sets the delay of each flight plan."""
    for key in fpDic:
        if fpDic.get(key) is not None:
            delay = int(key.split(':')[0]) * 60 + int(key.split(':')[1]) - (fpDic.get(key).get('aHour') * 60 + fpDic.get(key).get('aMin'))
            fpDic.get(key).update({'gDelay' : 0})
            fpDic.get(key).update({'aDelay' : 0})
            if fpDic.get(key).get('type') == 'Regulated':
                fpDic.get(key).update({'gDelay' : delay})
            else:
                fpDic.get(key).update({'aDelay' : delay})
    
    return fpDic


def getWP3Results():
    """Gets the results of WP3."""
    arrivals, HnoReg = main()
    arrivals = defineType(arrivals, rStart, rEnd, margin, radius, Hfile, HnoReg)
    fpDic = assignSlots(arrivals, getSlots(AAR, PAAR, rStart, rEnd))
    fpDic = filterFPs(fpDic, rStart, HnoReg)
    cost = cost_file("cost.ALL_FT+")
    buildMatrix(fpDic, cost)
    fpDic = setDelays(fpDic)
    x, y, fpDic = computePollution(fpDic)
    return fpDic


def calculateCostsFromWP2():
    """Calculates the cost of the flight plan assignment done in WP2."""
    fpDic = getWP2Results()
    cost = cost_file("cost.ALL_FT+")
    totalCost = 0
    keys = list(fpDic.keys())
    index = 0
    for key in fpDic:
        index += 1
        if fpDic.get(key) is None:
            continue
        
        if index == len(keys):
            totalCost += getCost(fpDic.get(key), key, key, cost)
        else:
            totalCost += getCost(fpDic.get(key), key, keys[index], cost)

    print(f'Total cost calculated from WP2: {round(totalCost, 2)} €')

# --------------------------------------------------------------------------------------------
# MAIN PROGRAM
do = False # Set to false to execute wp4

if do:
    arrivals, HnoReg = main()
    arrivals = defineType(arrivals, rStart, rEnd, margin, radius, Hfile, HnoReg)
    fpDic = assignSlots(arrivals, getSlots(AAR, PAAR, rStart, rEnd))
    fpDic = filterFPs(fpDic, rStart, HnoReg)
    cost = cost_file("cost.ALL_FT+")
    buildMatrix(fpDic, cost)
    setDelays(fpDic)
    calculateCostsFromWP2()
    

    