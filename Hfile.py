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
    return (speed / time)


def aggregateDemand():
    pass


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



# --------------------------------------------------------------------------------------------
# GLOBAL VARIABLES

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
# GET ALL THE FLIGHTS AND FILTER THEM TO ONLY ARRIVALS AT LEBL
arrivals = parse_allft_plus_file("20160129.ALL_FT+")
arrivals = filterData('LEBL')

# CHANGES THE TIME FORMAT
for i in range(len(arrivals)):
    arrivals[i] = changeTimeFormat(arrivals[i])
    isInECAC(arrivals[i])

hours = [i for i in range(0, 24)]

reducedCapacity = [i for i in range(12, 18)]
