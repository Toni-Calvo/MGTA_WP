from wp1 import main, isInECAC, getDistance, getSlots, plotSlotsArrOverTime

# --------------------------------------------------------------------------------------------
# GLOBAL VARIABLES

Hfile = 6 # h
AAR = 38
PAAR = 12
rStart = 8 # h
rEnd = 13 # h
margin = 30 # min
radius = 1500 # km

groundConsumption = {'A321' : '600 kg/h', 'A320' : '600 kg/h', 'B737' : '600 kg/h', 'B738' : '600 kg/h', 'C510' : '200 kg/h', 'PC12' : '200 kg/h', 'C25A' : '200 kg/h', 'B733' : '400 kg/h',
'A319' : '600 kg/h', 'E145' : '400 kg/h', 'E190' : '400 kg/h', 'LJ60' : '200 kg/h', 'B77W' : '1,000 kg/h', 'B350' : '200 kg/h', 'B764' : '800 kg/h', 'CRJX' : '400 kg/h',
'CRJ2' : '400 kg/h', 'B734' : '400 kg/h', 'F100' : '400 kg/h', 'B763' : '800 kg/h', 'B752' : '800 kg/h', 'A332' : '1,000 kg/h', 'A343' : '1,000 kg/h', 'F900' : '400 kg/h',
'B739' : '600 kg/h', 'AT75' : '400 kg/h', 'F2TH' : '400 kg/h', 'A333' : '1,000 kg/h', 'A388' : '1,350 kg/h', 'B77L' : '1,000 kg/h', 'GLF5' : '400 kg/h', 'E120' : '200 kg/h',
'H25B' : '200 kg/h', 'BE10' : '200 kg/h'
}

airConsumption = {'A321' : '3,500 kg/h', 'A320' : '3,500 kg/h', 'B737' : '3,500 kg/h', 'B738' : '3,500 kg/h', 'C510' : '1,000 kg/h', 'PC12' : '1,000 kg/h', 'C25A' : '1,000 kg/h', 'B733' : '2,000 kg/h',
'A319' : '3,500 kg/h', 'E145' : '2,000 kg/h', 'E190' : '2,000 kg/h', 'LJ60' : '1,000 kg/h', 'B77W' : '7,000 kg/h', 'B350' : '1,000 kg/h', 'B764' : '5,000 kg/h', 'CRJX' : '2,000 kg/h',
'CRJ2' : '2,000 kg/h', 'B734' : '2,000 kg/h', 'F100' : '2,000 kg/h', 'B763' : '5,000 kg/h', 'B752' : '5,000 kg/h', 'A332' : '7,000 kg/h', 'A343' : '7,000 kg/h', 'F900' : '2,000 kg/h',
'B739' : '3,500 kg/h', 'AT75' : '2,000 kg/h', 'F2TH' : '2,000 kg/h', 'A333' : '7,000 kg/h', 'A388' : '11,000 kg/h', 'B77L' : '7,000 kg/h', 'GLF5' : '2,000 kg/h', 'E120' : '1,000 kg/h',
'H25B' : '1,000 kg/h', 'BE10' : '1,000 kg/h'
}

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
            if fpDic.get(key).get('gDelay') != 0 and fpDic.get(key).get('CTD') < rStart * 60:
                delay += fpDic.get(key).get('gDelay')
    
    print(f'Unrecoverable ground delay applied before {rStart}:00: {delay} min')
                
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