import numpy as np
import math
import matplotlib.pyplot as plt
import random as rnd
from parse_allft import parse_allft_plus_file
# --------------------------------------------------------------------------------------------
# FUNCTIONS
def filterData(key, arrivals):
    """Returns the flight plans arriving at the key airport."""
    index = 0
    while index != len(arrivals):
        if arrivals[index].get('arrival_airport') == key:
            index += 1
        else:
            arrivals.remove(arrivals[index])
    
    return arrivals


def changeTimeFormat(flightPlan):
    """Changes the time format from yyyymmddhhmmss and updates the dictionary with 3 new keys (hour, min, sec) for arrivals and departures.
    Harcoded for UTC + 1."""
    time = int(flightPlan.pop('scheduled_arrival'))
    time = time - math.trunc(time / 1e6) * 1e6
    aHour = math.trunc(time / 1e4)
    aMin = math.trunc(time / 100) - aHour * 100
    aSec = int(time - aMin * 100 - aHour * 1e4)

    time = int(flightPlan.pop('scheduled_departure'))
    time = time - math.trunc(time / 1e6) * 1e6
    dHour = math.trunc(time / 1e4)
    dMin = math.trunc(time / 100) - dHour * 100
    dSec = int(time - dMin * 100 - dHour * 1e4)

    dic = {'aHour' : aHour + 1, 'aMin' : aMin, 'aSec' : aSec, 'dHour' : dHour + 1, 'dMin' : dMin, 'dSec' : dSec}
    flightPlan.update(dic)
    return flightPlan


def getArrMin(flightPlan):
    """Returns the flight plan arrival time in minutes."""
    min = flightPlan.get('aMin')
    hour = flightPlan.get('aHour')
    return (min + hour * 60)


def getDepMin(flightPlan):
    """Returns the flight plan depature time in minutes."""
    min = flightPlan.get('dMin')
    hour = flightPlan.get('dHour')
    return (min + hour * 60)
    

def getFlightTime(flightPlan):
    """Returns the flight time of the flight plan."""
    STD = getDepMin(flightPlan) + 15 # Taxi time = 15 min
    STA = getArrMin(flightPlan)
    return (STA - STD)


def getDistance(flightPlan):
    """Returns the distance of the flight plan."""
    time = getFlightTime(flightPlan)    # min
    speed = avSpeeds.get(flightPlan.get('aircraft_type'))
    speed /= 60 # km/h -> km/min
    return speed * time



def isInECAC(flightPlan):
    """Returns a boolean showing if the flight comes from the ECAC region."""
    depAirport = flightPlan.get('departure_airport')
    lDepAirport = list(depAirport)
    if (lDepAirport[0] + lDepAirport[1]) in ecacCodes:
        return True
    return False


def getCategory(flightPlan):
    """Returns the aircraft's cathegory of the flight plan."""
    aircraft = flightPlan.get('aircraft_type')
    return category.get(aircraft)


def getAvaliableSeats(flightPlan):
    """Returns the aircraft's total ammount of seats of the flight plan."""
    aircraft = flightPlan.get('aircraft_type')
    return seats.get(aircraft)


def getSlots(AAR, PAAR, rStart, rEnd):
    """Returns a vector of slots for nominal (AAR) and reduced (PAAR) capacity."""
    slots = []
    minAAR = 60 // AAR
    if 60 % AAR != 0:
        minAAR += 1
    minPAAR = 60 // PAAR
    if 60 % PAAR != 0:
        minPAAR += 1
    
    for i in range(0, 24):
        if rStart <= i < rEnd:
            for j in range(0, 60, minPAAR):
                slots.append((i * 60) + j)
        else:
            for j in range(0, 60, minAAR):
                slots.append((i * 60) + j)
    return slots


def assignSlots(flightPlans, slots):
    """Assigns slots to all the flight plans."""
    fpDic = {}
    fpList = flightPlans.copy()
    for slotIndex in range(len(slots) - 1):
        if (fpList[0].get('aHour') * 60 + fpList[0].get('aMin')) < slots[slotIndex + 1]:
            fpDic.update({str(slots[slotIndex] // 60) + ':' + str(slots[slotIndex] % 60) : fpList[0]})
            fpList.pop(0)
        else:
            fpDic.update({str(slots[slotIndex] // 60) + ':' + str(slots[slotIndex] % 60) : None})
        
    return fpDic


def sortByArrTime(flightPlans):
    """Sorts the flight plans by arrival time."""
    flightPlans.sort(key=lambda x: (x.get('aHour'), x.get('aMin')))
    return flightPlans


def plotOriginalArrOverTime(flightPlans, rStart, rEnd, AAR, PAAR, print):
    """Plots the ammount of arrivals over the time of the day."""
    x = [i for i in range(24)]
    y = [0] * 24
    for flightPlan in flightPlans:
        y[flightPlan.get('aHour')] += 1
    
    yAAR = []
    for i in range(0, 24):
        if rStart <= i < rEnd:
            yAAR.append(None)
        else:
            if 60 % AAR != 0:
                yAAR.append(((60//AAR) + 1)**-1 * 60)
            else:
                yAAR.append(AAR)
            
    yPAAR = []
    for i in range(0, 24):
        if rStart <= i < rEnd:
            if 60 % PAAR != 0:
                yPAAR.append(((60//PAAR) + 1)**-1 * 60)
            else:
                yPAAR.append(PAAR)
        else:
            yPAAR.append(None)
    
    if print:
        plt.plot(x,yAAR, color='green')
        plt.plot(x,yPAAR, color='red')
        plt.bar(x, y)
        plt.xlim(0, 24)
        plt.xticks(np.arange(0, 24, 1))
        plt.xlabel('Time of the day')
        plt.ylabel('# of arrivals')
        plt.show()


def plotSlotsArrOverTime(fpDic,print):
    """Plots the ammount of arrivals over the time of the day following the assigned slots."""
    x = [i for i in range(24)]
    y = [0] * 24
    for key in fpDic:
        if fpDic.get(key) != None:
            y[int(key.split(':')[0])] += 1
        
    if print:
        plt.bar(x, y)
        plt.xlim(0, 24)
        plt.xticks(np.arange(0, 24, 1))
        plt.xlabel('Time of the day')
        plt.ylabel('# of arrivals')
        plt.show()
        
    
def aggregateDelay(fpDic, HnoReg):
    """Returns the total delay of the day."""
    delay = 0
    for key in fpDic:
        if fpDic.get(key) != None:
            if fpDic.get(key).get('aHour') < HnoReg[0] or (fpDic.get(key).get('aHour') == HnoReg[0] and fpDic.get(key).get('aMin') < HnoReg[1]):
                addedDelay = (int(key.split(':')[0]) * 60 + int(key.split(':')[1])) - (fpDic.get(key).get('aHour') * 60 + fpDic.get(key).get('aMin'))
                if addedDelay > 0:
                    delay += addedDelay
                
    return delay


def plotAggregateDelay(fpDic, print):
    """Plots the aggregated delay over the time of the day."""
    x = []
    y = []
    delay = 0
    for key in fpDic:
        x.append(int(key.split(':')[0]) + int(key.split(':')[1])/60)
        if fpDic.get(key) != None:
            addedDelay = (int(key.split(':')[0]) * 60 + int(key.split(':')[1])) - (fpDic.get(key).get('aHour') * 60 + fpDic.get(key).get('aMin'))
            if addedDelay > 0:
                delay += addedDelay
                
        y.append(delay)
        
    if print:
        plt.plot(x, y)
        plt.xlim(0, 24)
        plt.xticks(np.arange(0, 24, 1))
        plt.xlabel('Time of the day')
        plt.ylabel('Delay [min]')
        plt.show()


def plotDemandAndCapacity(flightPlans, AAR, PAAR, rStart, rEnd, print):
    """Plots the demand and capacity over the time of the day."""
    x = [i for i in np.arange(0, 24, 1/60)]
    y = [0] * len(x)
    capacity = [0] * len(x)
    HnoReg = [24, 0]
    
    for flightPlan in flightPlans:
        index = flightPlan.get('aHour')*60 + flightPlan.get('aMin')
        while index < len(y):
            y[index] += 1
            index += 1
            
    if 60 % PAAR != 0:
        PSlot = 60 // PAAR + 1
    else:
        PSlot = 60 // PAAR
        
    if 60 % AAR != 0:
        ASlot = 60 // AAR + 1
    else:
        ASlot = 60 // AAR
        
    for i in range(len(capacity)):
        if rStart * 60 == i:
            capacity[i] = y[i]
        elif rStart * 60 < i < rEnd * 60:
            capacity[i] = capacity[i - 1] + int(10/PSlot)/10
        elif rEnd * 60 <= i:
            capacity[i] = capacity[i - 1] + int(10/ASlot)/10
            if capacity[i] > y[i]:
                capacity[i] = y[i]
                HnoReg = [i//60, i%60]
                for k in range(i + 1, len(capacity)):
                    capacity[k] = None
                break
        else:
            capacity[i] = None
    
    if print:          
        plt.plot(x, y)
        plt.plot(x, capacity, color='red')
        plt.xlim(0, 24)
        plt.xticks(np.arange(0, 24, 1))
        plt.xlabel('Time of the day')
        plt.ylabel('Demand')
        plt.show()
        
    return HnoReg


def affectedFlights(rStart, HnoReg, fpDic):
    """Returns the ammount of affected flights by the GDP."""
    affected = 0
    for key in fpDic:
        if fpDic.get(key) != None:
            if rStart * 60 < (int(key.split(':')[0]) * 60 + int(key.split(':')[1])) <= (HnoReg[0] * 60 + HnoReg[1]):
                affected += 1
    
    return affected
            
# --------------------------------------------------------------------------------------------
# GLOBAL VARIABLES

Hfile = 6
AAR = 38
PAAR = 12
rStart = 8
rEnd = 13

avSpeeds = {'A321' : 833, 'A320' : 962, 'B737' : 912, 'B738' : 853, 'C510' : 478, 'PC12' : 528, 'C25A' : 426, 'B733' : 794,
            'A319' : 828, 'E145' : 814, 'E190' : 829, 'LJ60' : 778, 'B77W' : 907, 'B350' : 518, 'B764' : 851, 'CRJX' : 830,
            'CRJ2' : 810, 'B734' : 796, 'F100' : 750, 'B763' : 851, 'B752' : 870, 'A332' : 871, 'A343' : 871, 'F900' : 944,
            'B739' : 851, 'AT75' : 518, 'F2TH' : 870, 'A333' : 871, 'A388' : 963, 'B77L' : 907, 'GLF5' : 888, 'E120' : 552,
            'H25B' : 537, 'BE10' : 407}

ecacCodes = ['LA', 'UD', 'LO', 'UB', 'EB', 'LQ', 'LB', 'LD', 'LC', 'LK', 'EK', 'EE', 'EF', 'LF', 'UG', 'ED', 'LG', 'LH', 'BI',
             'EI', 'LI', 'EV', 'EY', 'EL', 'LM', 'LN', 'LY', 'EH', 'LW', 'EN', 'EP', 'LP', 'LU', 'LR', 'LI', 'LY', 'LZ', 'LJ',
             'LE', 'ES', 'LS', 'LT', 'UK', 'EG']

category = {'A321' : 'D', 'A320' : 'D', 'B737' : 'D', 'B738' : 'D', 'C510' : 'F', 'PC12' : 'F', 'C25A' : 'F', 'B733' : 'E',
            'A319' : 'D', 'E145' : 'E', 'E190' : 'E', 'LJ60' : 'F', 'B77W' : 'B', 'B350' : 'F', 'B764' : 'C', 'CRJX' : 'E',
            'CRJ2' : 'E', 'B734' : 'E', 'F100' : 'E', 'B763' : 'C', 'B752' : 'C', 'A332' : 'B', 'A343' : 'B', 'F900' : 'E',
            'B739' : 'D', 'AT75' : 'E', 'F2TH' : 'E', 'A333' : 'B', 'A388' : 'A', 'B77L' : 'B', 'GLF5' : 'E', 'E120' : 'F',
            'H25B' : 'F', 'BE10' : 'F'}

seats = {'A321' : 220, 'A320' : 180, 'B737' : 189, 'B738' : 181, 'C510' : 4, 'PC12' : 8, 'C25A' : 7, 'B733' : 149,
         'A319' : 144, 'E145' : 50, 'E190' : 100, 'LJ60' : 8, 'B77W' : 212, 'B350' : 12, 'B764' : 156, 'CRJX' : 100,
         'CRJ2' : 50, 'B734' : 188, 'F100' : 100, 'B763' : 184, 'B752' : 233, 'A332' : 288, 'A343' : 249, 'F900' : 14,
         'B739' : 167, 'AT75' : 78, 'F2TH' : 19, 'A333' : 292, 'A388' : 520, 'B77L' : 238, 'GLF5' : 19, 'E120' : 30,
         'H25B' : 14, 'BE10' : 15}

# --------------------------------------------------------------------------------------------
# MAIN PROGRAM
def main(plot=False):
    """Returns arrivals ordered by arrival time."""
    # GET ALL THE FLIGHTS AND FILTER THEM TO ONLY ARRIVALS AT LEBL
    arrivals = parse_allft_plus_file("20160129.ALL_FT+")
    arrivals = filterData('LEBL', arrivals)

    # CHANGES THE TIME FORMAT
    for i in range(len(arrivals)):
        arrivals[i] = changeTimeFormat(arrivals[i])
        
        
    arrivals = sortByArrTime(arrivals)
    
    # REMOVE FLIGHTS +24H
    index = 0
    while index != len(arrivals):
        if arrivals[index].get('aHour') < 24:
            index += 1
        else:
            arrivals.remove(arrivals[index])
        
    fpDic = assignSlots(arrivals, getSlots(AAR, PAAR, rStart, rEnd))
    plotOriginalArrOverTime(arrivals, rStart, rEnd, AAR, PAAR, plot)
    plotSlotsArrOverTime(fpDic, plot)

    plotAggregateDelay(fpDic, plot)
    HnoReg = plotDemandAndCapacity(arrivals, AAR, PAAR, rStart, rEnd, plot)
    #print(aggregateDelay(fpDic, HnoReg))
    #print(affectedFlights(rStart, HnoReg, fpDic))
    return arrivals, HnoReg

main()