import numpy as np
import math
import matplotlib.pyplot as plt
import random as rnd
from parse_allft import parse_allft_plus_file

# --------------------------------------------------------------------------------------------
# FUNCTIONS
def filterData(key):
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
    Harcoded to UTC + 1."""
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
    """Returns the distance of the flight plan"""
    time = getFlightTime(flightPlan)
    pass

    #return (speed / time)


def aggregateDemand():
    pass


# --------------------------------------------------------------------------------------------
# GLOBAL VARIABLES

category = {'A321' : 'D', 'A320' : 'D', 'B737' : 'D', 'B738' : 'D', 'C510' : 'F', 'PC12' : 'F', 'C25A' : 'F', 'B733' : 'E',
            'A319' : 'D', 'E145' : 'E', 'E190' : 'E', 'LJ60' : 'F', 'B77W' : 'B', 'B350' : 'F', 'B764' : 'C', 'CRJX' : 'E',
            'CRJ2' : 'E', 'B734' : 'E', 'F100' : 'E', 'B763' : 'C', 'B752' : 'C', 'A332' : 'B', 'A343' : 'B', 'F900' : 'E',
            'B739' : 'D', 'AT75' : 'E', 'F2TH' : 'E', 'A333' : 'B', 'A388' : 'A', 'B77L' : 'B', 'GLF5' : 'E', 'E120' : 'F',
            'H25B' : 'F', 'BE10' : 'F'}
# --------------------------------------------------------------------------------------------
# MAIN PROGRAM
# GET ALL THE FLIGHTS AND FILTER THEM TO ONLY ARRIVALS AT LEBL
arrivals = parse_allft_plus_file("20160129.ALL_FT+")
arrivals = filterData('LEBL')

# CHANGES THE TIME FORMAT
for i in range(len(arrivals)):
    arrivals[i] = changeTimeFormat(arrivals[i])

aviones = []
for k in arrivals:
    avion = k.get('aircraft_type')
    if avion not in aviones:
        aviones.append(avion)

print(aviones)

hours = [i for i in range(0, 24)]

reducedCapacity = [i for i in range(12, 18)]
