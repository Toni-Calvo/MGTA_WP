from wp1 import main, isInECAC, getDistance, getSlots, plotSlotsArrOverTime

# --------------------------------------------------------------------------------------------
# GLOBAL VARIABLES

Hfile = 6 # h
AAR = 38    # NOMINAL CAPACITY
PAAR = 12   # REDUCED CAPACITY
rStart = 8 # h
rEnd = 13 # h
margin = 30 # min DO NOT CHANGE
radius = 1500 # km
CO2Factor = 3.16 # kg CO2 / kg fuel
cancelledAirline = 'VLG'
maxDelay = 190 # min

groundConsumption = {'A321' : 600, 'A320' : 600, 'B737' : 600, 'B738' : 600, 'C510' : 200, 'PC12' : 200, 'C25A' : 200, 'B733' : 400,
                     'A319' : 600, 'E145' : 400, 'E190' : 400, 'LJ60' : 200, 'B77W' : 1000, 'B350' : 200, 'B764' : 800, 'CRJX' : 400,
                     'CRJ2' : 400, 'B734' : 400, 'F100' : 400, 'B763' : 800, 'B752' : 800, 'A332' : 1000, 'A343' : 1000, 'F900' : 400,
                     'B739' : 600, 'AT75' : 400, 'F2TH' : 400, 'A333' : 1000, 'A388' : 1350, 'B77L' : 1000, 'GLF5' : 400, 'E120' : 200,
                     'H25B' : 200, 'BE10' : 200}

airConsumption = {'A321' : 3500, 'A320' : 3500, 'B737' : 3500, 'B738' : 3500, 'C510' : 1000, 'PC12' : 1000, 'C25A' : 1000, 'B733' : 2000,
                  'A319' : 3500, 'E145' : 2000, 'E190' : 2000, 'LJ60' : 1000, 'B77W' : 7000, 'B350' : 1000, 'B764' : 5000, 'CRJX' : 2000,
                  'CRJ2' : 2000, 'B734' : 2000, 'F100' : 2000, 'B763' : 5000, 'B752' : 5000, 'A332' : 7000, 'A343' : 7000, 'F900' : 2000,
                  'B739' : 3500, 'AT75' : 2000, 'F2TH' : 2000, 'A333' : 7000, 'A388' : 11000, 'B77L' : 7000, 'GLF5' : 2000, 'E120' : 1000,
                  'H25B' : 1000, 'BE10' : 1000}

# --------------------------------------------------------------------------------------------
# FUNCTIONS
             
def defineType(flightPlans, rStart, rEnd, margin, radius, Hfile, HnoReg):
    """Defines the type of the flight plan."""
    rStart *= 60
    rEnd *= 60
    for flightPlan in flightPlans:
        departure = flightPlan.get('dHour') * 60 + flightPlan.get('dMin')
        arrival = flightPlan.get('aHour') * 60 + flightPlan.get('aMin')
        if arrival < rStart or arrival >= HnoReg[0]*60 + HnoReg[1]:
            flightPlan.update({'type' : 'Not affected'})
        else:
            if departure < Hfile + margin:
                flightPlan.update({'type' : 'Exempt'})
            elif not isInECAC(flightPlan) or getDistance(flightPlan) > radius:
                flightPlan.update({'type' : 'Exempt'})
            else:
                flightPlan.update({'type' : 'Regulated'})
        
    return flightPlans


def separateFlights(flightPlans):
    """Separates the flight plans into exempt and the rest."""
    exemptFlights = []
    restFlights = []
    for flightPlan in flightPlans:
        if flightPlan.get('type') == 'Exempt':
            exemptFlights.append(flightPlan)
        else:
            restFlights.append(flightPlan)
            
    return exemptFlights, restFlights


def assignSlots(exemptFlights, restFlights, slots):
    """Assigns slots to all the flight plans, taking into consideration the GDP."""
    fpDic = {}
    fpList = exemptFlights.copy()
    for slotIndex in range(len(slots) - 1):
        if (fpList[0].get('aHour') * 60 + fpList[0].get('aMin')) < slots[slotIndex + 1]:
            fpDic.update({str(slots[slotIndex] // 60) + ':' + str(slots[slotIndex] % 60) : fpList[0]})
            fpList.pop(0)
            if fpList == []:
                break
        else:
            fpDic.update({str(slots[slotIndex] // 60) + ':' + str(slots[slotIndex] % 60) : None})
    
    
    fpList = restFlights.copy()
    for slotIndex in range(len(slots) - 1):
        if (fpList[0].get('aHour') * 60 + fpList[0].get('aMin')) < slots[slotIndex + 1] and fpDic.get(str(slots[slotIndex] // 60) + ':' + str(slots[slotIndex] % 60)) == None:
            fpDic.update({str(slots[slotIndex] // 60) + ':' + str(slots[slotIndex] % 60) : fpList[0]})
            fpList.pop(0)
            if fpList == []:
                break
            
    return fpDic


def computeTotalDelays(fpDic):
    """Computes the delay for each flight plan and returns the flightPlans, the total exempt, ground, and not affected delay."""
    totalExemptDelay = 0
    totalNotAffectedDelay = 0
    totalGroundDelay = 0
    
    for key in fpDic:
        if fpDic.get(key) != None:
            delay = int(key.split(':')[0]) * 60 + int(key.split(':')[1]) - (fpDic.get(key).get('aHour') * 60 + fpDic.get(key).get('aMin'))
            if delay < 0:
                fpDic.get(key).update({'gDelay' : 0})
                fpDic.get(key).update({'aDelay' : 0})
            else:
                if fpDic.get(key).get('type') == 'Regulated':
                    fpDic.get(key).update({'gDelay' : delay})
                    fpDic.get(key).update({'aDelay' : 0})
                    totalGroundDelay += delay
                else:
                    fpDic.get(key).update({'gDelay' : 0})
                    fpDic.get(key).update({'aDelay' : delay})
                    if fpDic.get(key).get('type') == 'Exempt':
                        totalExemptDelay += delay
                    else:
                        totalNotAffectedDelay += delay
    
    return fpDic, totalExemptDelay, totalGroundDelay, totalNotAffectedDelay


def printFlightTypes(fpDic):
    """Prints the ammount of Flight Plans of each type."""
    notAffected = 0
    exempt = 0
    regulated = 0
    
    for key in fpDic:
        if fpDic.get(key) != None:
            if fpDic.get(key).get('type') == 'Not affected':
                notAffected += 1
            elif fpDic.get(key).get('type') == 'Exempt':
                exempt += 1
            else:
                regulated += 1
    
    print(f'Not affected: {notAffected}\nExempt: {exempt}\nRegulated: {regulated}')


def assignCTAandCTD(fpDic):
    """Assigns the CTA and CTD to each flight plan."""
    for key in fpDic:
        if fpDic.get(key) != None:
            if fpDic.get(key).get('gDelay') != 0:
                fpDic.get(key).update({'CTA' : int(key.split(':')[0]) * 60 + int(key.split(':')[1])})
                fpDic.get(key).update({'CTD' : fpDic.get(key).get('dHour') * 60 + fpDic.get(key).get('dMin') + fpDic.get(key).get('gDelay')})
            if fpDic.get(key).get('aDelay') != 0:
                fpDic.get(key).update({'CTA' : int(key.split(':')[0]) * 60 + int(key.split(':')[1])})
                fpDic.get(key).update({'CTD' : fpDic.get(key).get('dHour') * 60 + fpDic.get(key).get('dMin')})
            else:
                fpDic.get(key).update({'CTA' : fpDic.get(key).get('aHour') * 60 + fpDic.get(key).get('aMin')})
                fpDic.get(key).update({'CTD' : fpDic.get(key).get('dHour') * 60 + fpDic.get(key).get('dMin')})
                
    return fpDic


def printUnrecGDelay(fpDic, rStart):
    """Prints the unrecoverable ground delay applied before rStart"""
    delay = 0
    for key in fpDic:
        if fpDic.get(key) != None:
            if fpDic.get(key).get('gDelay') != 0:
                if fpDic.get(key).get('CTD') < rStart * 60:
                    delay += fpDic.get(key).get('gDelay')
                elif fpDic.get(key).get('dHour') * 60 + fpDic.get(key).get('dMin') < rStart * 60:
                    delay += abs(fpDic.get(key).get('dHour') * 60 + fpDic.get(key).get('dMin') - rStart * 60)
    
    print(f'Unrecoverable ground delay applied before {rStart}:00: {delay} min')


def computePollution(fpDic):
    """Computes the pollution due to the regulation."""
    totalPollutionAir = 0
    totalPollutionGround = 0
    for key in fpDic:
        if fpDic.get(key) != None:
            if fpDic.get(key).get('type') == 'Exempt' and fpDic.get(key).get('aDelay') != 0:
                totalPollutionAir += airConsumption.get(fpDic.get(key).get('aircraft_type')) * (fpDic.get(key).get('aDelay') / 60) * CO2Factor
            if fpDic.get(key).get('type') == 'Regulated' and fpDic.get(key).get('gDelay') != 0:
                totalPollutionGround += groundConsumption.get(fpDic.get(key).get('aircraft_type')) * (fpDic.get(key).get('gDelay') / 60) * CO2Factor
    
    print(f'Total kg of CO2 of air delay: {totalPollutionAir}\nTotal kg of CO2 of ground delay: {totalPollutionGround}')


def cancelledFlights(fpDic, cancelledAirline, maxDelay, slots):
    """A new assignation of slots without the cancelled flights."""
    # Detect cancelled flights
    cancelled = []
    for key in fpDic:
        if fpDic.get(key) != None:
            if fpDic.get(key).get('airline_code') == cancelledAirline:
                if fpDic.get(key).get('gDelay') > maxDelay or fpDic.get(key).get('aDelay') > maxDelay:
                    fpDic.get(key).update({'type' : 'Cancelled'})
                    cancelled.append(key)
    
    print(f'Cancelled flights: {len(cancelled)}')
    
    notAssigned = cancelled.copy()
    # Assign reserved slots
    for slotIndex in range(len(slots) - 1):
        key = str(slots[slotIndex] // 60) + ':' + str(slots[slotIndex] % 60)
        nextKey = str(slots[slotIndex + 1] // 60) + ':' + str(slots[slotIndex + 1] % 60)
        
        if fpDic.get(key) == None:
            continue
        
        if key in notAssigned:
            nextFPkey = getNextFPNotCancelled(fpDic, slotIndex, slots, cancelledAirline)
            if canMoveSlot(nextKey, fpDic.get(nextFPkey)):
                fpDic.update({key : fpDic.get(nextFPkey)})
                fpDic.update({nextFPkey : None})
            else:
                fpDic.update({key : None})
                
            notAssigned.remove(key)
        
        if len(notAssigned) == 0:
            break
        
    # Compress
    for slotIndex in range(1, len(slots) - 1):
        key = str(slots[slotIndex] // 60) + ':' + str(slots[slotIndex] % 60)
        prevKey = str(slots[slotIndex - 1] // 60) + ':' + str(slots[slotIndex - 1] % 60)
        
        if fpDic.get(key) == None:
            continue
    
        bestKey = getBestEmptySlot(fpDic, slots, slotIndex, fpDic.get(key))
        if bestKey != key:
            fpDic.update({bestKey : fpDic.get(key)})
            fpDic.update({key : None})
                
    return fpDic
        
        
def getNextFPNotCancelled(fpDic, slotIndex, slots, cancelledAirline):
    """Returns the next flight plan that is not cancelled."""
    for slotIndex2 in range(slotIndex + 1, len(slots) - 1):
        key = str(slots[slotIndex2] // 60) + ':' + str(slots[slotIndex2] % 60)
        if fpDic.get(key) != None:
            if fpDic.get(key).get('airline_code') == cancelledAirline and fpDic.get(key).get('type') == 'Regulated':
                return key
    

def canMoveSlot(objectiveSlot, flightPlan):
    """Returns True if the flight plan can be moved to the objective slot."""
    time = int(objectiveSlot.split(':')[0]) * 60 + int(objectiveSlot.split(':')[1])
    if flightPlan.get('aHour') * 60 + flightPlan.get('aMin') < time:
        return True
    
    return False


def getBestEmptySlot(fpDic, slots, slotsIndex, flightPlan):
    """Returns the best empty slot for a flight plan."""
    for slotIndex in range(slotsIndex + 1):
        key = str(slots[slotIndex] // 60) + ':' + str(slots[slotIndex] % 60)
        nextKey = str(slots[slotIndex + 1] // 60) + ':' + str(slots[slotIndex + 1] % 60)
        if fpDic.get(key) == None:
            if canMoveSlot(nextKey, flightPlan):
                return key
    
    return key


def computeRelativeStandardDeviation(fpDic, totalGroundDelay, totalAirDelay):
    """Returns the relative standard devitation."""
    
    number_GroundFlights = getGroundFlights(fpDic)
    number_AirFlights = getExemptFlights(fpDic)

    mean_GroundDelay = totalGroundDelay/number_GroundFlights
    mean_AirDelay = totalAirDelay/number_AirFlights

    squareSum_Ground = 0
    squareSum_Air = 0

    for key in fpDic:
        if fpDic.get(key) != None:
            if fpDic.get(key).get('type')=='Regulated':
                squareSum_Ground += (fpDic.get(key).get('gDelay'))**2
            if fpDic.get(key).get('type')=='Exempt':
                squareSum_Air += (fpDic.get(key).get('aDelay'))**2

    standardDeviation_Total = ((squareSum_Ground + squareSum_Air)/(number_GroundFlights + number_AirFlights-1))**0.5

    standardDeviation_GroundDelay = ((squareSum_Ground)/(number_GroundFlights - 1))**0.5
    standardDeviation_AirDelay = ((squareSum_Air)/(number_AirFlights - 1))**0.5
    
    relativeStandardDeviation_GroundDelay = (standardDeviation_GroundDelay/mean_GroundDelay)*100
    relativeStandardDeviation_AirDelay = (standardDeviation_AirDelay/mean_AirDelay)*100

    return relativeStandardDeviation_GroundDelay, relativeStandardDeviation_AirDelay, standardDeviation_Total


def getGroundFlights(fpDic):
    """Returns the total flights in ground."""
    count = 0
    for key in fpDic:
        if fpDic.get(key) != None:
            if fpDic.get(key).get('type')=='Regulated':
                count += 1
                
    return count


def getExemptFlights(fpDic):
    """Returns the total flights in air."""
    count = 0
    for key in fpDic:
        if fpDic.get(key) != None:
            if fpDic.get(key).get('type')=='Exempt':
                count += 1
                
    return count


def numberFlightsDelayed(fpDic):
    """Returns the number of flights delayed (ground, air and total)."""
    n_DelayedGroundFlights = 0
    n_DelayedAirFlights = 0
    for key in fpDic:
        if fpDic.get(key) != None:
            if fpDic.get(key).get('gDelay') != 0:
                n_DelayedGroundFlights += 1
            if fpDic.get(key).get('aDelay') != 0:
                n_DelayedAirFlights += 1
    n_DelayedTotal = n_DelayedGroundFlights + n_DelayedAirFlights
    
    return n_DelayedGroundFlights, n_DelayedAirFlights, n_DelayedTotal


def numberFlightsDelayedPlus15min(fpDic):
    """Returns the number of flights delayed more than 15 minutes (ground, air and total)."""
    n_DelayedGroundFlights15 = 0
    n_DelayedAirFlights15 = 0
    for key in fpDic:
        if fpDic.get(key) != None:
            if fpDic.get(key).get('gDelay') > 15:
                n_DelayedGroundFlights15 += 1
            if fpDic.get(key).get('aDelay') > 15:
                n_DelayedAirFlights15 += 1
    n_DelayedTotal15 = n_DelayedGroundFlights15 + n_DelayedAirFlights15
    
    return n_DelayedGroundFlights15, n_DelayedAirFlights15, n_DelayedTotal15


def maximumDelay(fpDic):
    maxDelayGround = 0
    maxDelayAir = 0
    maxDelayTotal = 0
    for key in fpDic:
        if fpDic.get(key) != None:
            if fpDic.get(key).get('gDelay') > maxDelayGround:
                maxDelayGround = fpDic.get(key).get('gDelay')
            if fpDic.get(key).get('aDelay') > maxDelayAir:
                maxDelayAir = fpDic.get(key).get('aDelay')
    if maxDelayAir > maxDelayGround:
        maxDelayTotal = maxDelayAir
    else:
        maxDelayTotal = maxDelayGround
        
    return maxDelayGround, maxDelayAir, maxDelayTotal      
# --------------------------------------------------------------------------------------------
# MAIN PROGRAM

arrivals, HnoReg = main()
slots = getSlots(AAR, PAAR, rStart, rEnd)
arrivals = defineType(arrivals, rStart, rEnd, margin, radius, Hfile, HnoReg)
exempt, rest = separateFlights(arrivals)
fpDic = assignSlots(exempt, rest, slots)

fpDic, totalExemptDelay, totalGroundDelay, totalNotAffectedDelay = computeTotalDelays(fpDic)
print(f'Total exempt delay: {totalExemptDelay} min\nTotal ground delay: {totalGroundDelay} min\nTotal not affected delay: {totalNotAffectedDelay} min')
plotSlotsArrOverTime(fpDic, True)
printFlightTypes(fpDic)
fpDic = assignCTAandCTD(fpDic)
printUnrecGDelay(fpDic, rStart)
computePollution(fpDic)
stdev_Ground, stdev_Air, stdev_Total = computeRelativeStandardDeviation (fpDic,totalGroundDelay,totalExemptDelay)
print(f'Relative Standard Ground Delay Deviation: {stdev_Ground}%\nRelative Standard Air Delay Deviation: {stdev_Air}%\nRelative Standard Total Deviation: {stdev_Total}%')
nd_Ground, nd_Air, nd_Total = numberFlightsDelayed(fpDic)
print(f'Ground Delayed Flights: {nd_Ground} aircrafts\nAir Delayed Flights: {nd_Air} aircrafts\nTotal Delayed Flights: {nd_Total} aircrafts')
nd_Ground15, nd_Air15, nd_Total15 = numberFlightsDelayedPlus15min(fpDic)
print(f'Ground Delayed Flights >15 min: {nd_Ground15} aircrafts\nAir Delayed Flights >15 min: {nd_Air15} aircrafts\nTotal Delayed Flights >15 min: {nd_Total15} aircrafts')
maxGD, maxAD, maxTD = maximumDelay(fpDic)
print(f'Maximum Ground Delay: {maxGD} min\nMaximum Air Delay: {maxAD} min\nMaximum Delay: {maxTD} min')
av_GroundDelay = totalGroundDelay/nd_Ground
av_AirDelay = totalExemptDelay/nd_Air
av_TotalDelay = (totalExemptDelay+totalGroundDelay)/nd_Total
print(f'Average Ground Delay: {round(av_GroundDelay)} min/ac\nAverage Air Delay: {round(av_AirDelay)} min/ac\nAverage Total Delay: {round(av_TotalDelay)} min/ac')


# Cancelled flights (Not need for metrics yet)
print('\n\n\n')
cancelledFlights(fpDic, cancelledAirline, maxDelay, slots)
fpDic, totalExemptDelay, totalGroundDelay, totalNotAffectedDelay = computeTotalDelays(fpDic)
print(f'Total exempt delay: {totalExemptDelay} min\nTotal ground delay: {totalGroundDelay} min\nTotal not affected delay: {totalNotAffectedDelay} min')
fpDic = assignCTAandCTD(fpDic)
printUnrecGDelay(fpDic, rStart)
computePollution(fpDic)
stdev_Ground, stdev_Air, stdev_Total= computeRelativeStandardDeviation (fpDic,totalGroundDelay,totalExemptDelay)
print(f'Relative Standard Ground Delay Deviation: {stdev_Ground}%\nRelative Standard Air Delay Deviation: {stdev_Air}%\nRelative Standard Total Deviation: {stdev_Total}%')
nd_Ground, nd_Air, nd_Total = numberFlightsDelayed(fpDic)
print(f'Ground Delayed Flights: {nd_Ground} aircrafts\nAir Delayed Flights: {nd_Air} aircrafts\nTotal Delayed Flights: {nd_Total} aircrafts')
nd_Ground15, nd_Air15, nd_Total15 = numberFlightsDelayedPlus15min(fpDic)
print(f'Ground Delayed Flights >15 min: {nd_Ground15} aircrafts\nAir Delayed Flights >15 min: {nd_Air15} aircrafts\nTotal Delayed Flights >15 min: {nd_Total15} aircrafts')
maxGD, maxAD, maxTD = maximumDelay(fpDic)
print(f'Maximum Ground Delay: {maxGD} min\nMaximum Air Delay: {maxAD} min\nMaximum Delay: {maxTD} min')
av_GroundDelay = totalGroundDelay/nd_Ground
av_AirDelay = totalExemptDelay/nd_Air
av_TotalDelay = (totalExemptDelay+totalGroundDelay)/nd_Total
print(f'Average Ground Delay: {round(av_GroundDelay)} min/ac\nAverage Air Delay: {round(av_AirDelay)} min/ac\nAverage Total Delay: {round(av_TotalDelay)} min/ac')
