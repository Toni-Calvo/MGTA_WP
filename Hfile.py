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

speeds = {'A321' : 833, 'A320' : 962, 'B737' : 912, 'B738' : 853, 'C510' : 478, 'PC12' : 528, 'C25A' : 426, 'B733' : 794,
          'A319' : 828, 'E145' : 814, 'E190' : 829, 'LJ60' : 778, 'B77W' : 907, 'B350' : 518, 'B764' : 851, 'CRJX' : 830,
          'CRJ2' : 810, 'B734' : 796, 'F100' : 750, 'B763' : 851, 'B752' : 870, 'A332' : 871, 'A343' : 871, 'F900' : 944,
          'B739' : 851, 'AT75' : 518, 'F2TH' : 870, 'A333' : 871, 'A388' : 963, 'B77L' : 907, 'GLF5' : 888, 'E120' : 552,
          'H25B' : 537, 'BE10' : 407}
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
