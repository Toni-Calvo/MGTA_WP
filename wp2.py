from Hfile import main, isInECAC, getDistance, getSlots, plotSlotsArrOverTime

# --------------------------------------------------------------------------------------------
# GLOBAL VARIABLES

Hfile = 6 # h
AAR = 38
PAAR = 12
rStart = 8 # h
rEnd = 13 # h
margin = 30 # min
radius = 1500 # km

distanceAirport = {'UUEE', 'LROP', 'DAAG', 'LFRI', 'ENGM', 'LIML', 'EDQA', 'ESGG', 'EDDF', 'EVRA', 'GCLP', 'EDDV', 'ELLX', 'LHBP', 'EDDM', 'EKCH', 'LEMD', 'EDDH', 'EIDW', 'LFPO', 'LSGG', 'EDDT', 'LESO', 'LEST', 'EHAM', 'LEPA', 'LEMH', 'LEAL', 'LEBB', 'LPPT', 'EGKK', 'LECO', 'LEMG', 'LEZL', 'EBBR', 'LEIB', 'LIMC', 'LIRF', 'LLBG', 'LEGR', 'LEVX', 'LEAS', 'LFPG', 'SBGR', 'LSZH', 'LGAV', 'GCXO', 'EGBB', 'GMMN', 'LRTR', 'LFSB', 'EDDB', 'KEWR', 'EGCC', 'EGLL', 'LKPR', 'EBLG', 'LTFJ', 'LOWW', 'LPPR', 'GCTS', 'KJFK', 'EPWA', 'LFLL', 'LIPZ', 'EGPH', 'LFML', 'EHEH', 'LFRN', 'LIRN', 'SAEZ', 'GCRR', 'ESSA', 'EBOS', 'EDDP', 'EDDK', 'EDDL', 'LIBD', 'EDDS', 'LEVD', 'EGSS', 'LICJ', 'LIME', 'OTHH', 'EHRD', 'LFOB', 'EGGP', 'LEVC', 'EPMO', 'LFBD', 'LEAM', 'LTBA', 'LRCL', 'LIMF', 'SKBO', 'LFMN', 'HECA', 'LBSF', 'OMDB', 'EBAW', 'GMFF', 'LIRQ', 'LEXJ', 'EGNT', 'EGGW', 'EGGD', 'EGNM', 'LFRS', 'LEJR', 'GMMX', 'LIRP', 'LIPE', 'GMMW', 'DTTA', 'LIPH', 'LELN', 'EFHK', 'LEZG', 'LFLI', 'GCFV', 'GMTT'}

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


def computeDelay(fpDic):
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
# --------------------------------------------------------------------------------------------
# MAIN PROGRAM

arrivals, HnoReg = main()
slots = getSlots(AAR, PAAR, rStart, rEnd)
arrivals = defineType(arrivals, rStart, rEnd, margin, radius, Hfile, HnoReg)
exempt, rest = separateFlights(arrivals)
fpDic = assignSlots(exempt, rest, slots)

fpDic, totalExemptDelay, totalGroundDelay, totalNotAffectedDelay = computeDelay(fpDic)
print(f'Total exempt delay: {totalExemptDelay} min\nTotal ground delay: {totalGroundDelay} min\nTotal not affected delay: {totalNotAffectedDelay} min')
plotSlotsArrOverTime(fpDic, True)
