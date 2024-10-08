from Hfile import main, isInECAC, getDistance, getSlots

# --------------------------------------------------------------------------------------------
# GLOBAL VARIABLES

AAR = 38
PAAR = 12
rStart = 8
rEnd = 12
margin = 30
radius = 500 # km

distanceAirport = {'UUEE', 'LROP', 'DAAG', 'LFRI', 'ENGM', 'LIML', 'EDQA', 'ESGG', 'EDDF', 'EVRA', 'GCLP', 'EDDV', 'ELLX', 'LHBP', 'EDDM', 'EKCH', 'LEMD', 'EDDH', 'EIDW', 'LFPO', 'LSGG', 'EDDT', 'LESO', 'LEST', 'EHAM', 'LEPA', 'LEMH', 'LEAL', 'LEBB', 'LPPT', 'EGKK', 'LECO', 'LEMG', 'LEZL', 'EBBR', 'LEIB', 'LIMC', 'LIRF', 'LLBG', 'LEGR', 'LEVX', 'LEAS', 'LFPG', 'SBGR', 'LSZH', 'LGAV', 'GCXO', 'EGBB', 'GMMN', 'LRTR', 'LFSB', 'EDDB', 'KEWR', 'EGCC', 'EGLL', 'LKPR', 'EBLG', 'LTFJ', 'LOWW', 'LPPR', 'GCTS', 'KJFK', 'EPWA', 'LFLL', 'LIPZ', 'EGPH', 'LFML', 'EHEH', 'LFRN', 'LIRN', 'SAEZ', 'GCRR', 'ESSA', 'EBOS', 'EDDP', 'EDDK', 'EDDL', 'LIBD', 'EDDS', 'LEVD', 'EGSS', 'LICJ', 'LIME', 'OTHH', 'EHRD', 'LFOB', 'EGGP', 'LEVC', 'EPMO', 'LFBD', 'LEAM', 'LTBA', 'LRCL', 'LIMF', 'SKBO', 'LFMN', 'HECA', 'LBSF', 'OMDB', 'EBAW', 'GMFF', 'LIRQ', 'LEXJ', 'EGNT', 'EGGW', 'EGGD', 'EGNM', 'LFRS', 'LEJR', 'GMMX', 'LIRP', 'LIPE', 'GMMW', 'DTTA', 'LIPH', 'LELN', 'EFHK', 'LEZG', 'LFLI', 'GCFV', 'GMTT'}

# --------------------------------------------------------------------------------------------
# FUNCTIONS
             
def defineType(flightPlans, rStart, rEnd, margin, radius):
    """Defines the type of the flight plan."""
    for flightPlan in flightPlans:
        departure = flightPlan.get('dHour') * 60 + flightPlan.get('dMin')
        if rStart >= departure or departure >= rEnd:
            flightPlan.update({'type' : 'Not affected'})
        elif rStart + margin >= departure:
            flightPlan.update({'type' : 'Exempt'})
        else:
            if not isInECAC(flightPlan) or getDistance(flightPlan) > radius:
                flightPlan.update({'type' : 'Exempt'})
            else:    
                flightPlan.update({'type' : 'Regulated'})


def assignSlots(flightPlans, slots):
    """Assigns slots to all the flight plans, taking into consideration the GDP."""
    fpDic = {}
    fpList = flightPlans.copy()
    for slotIndex in range(len(slots) - 1):
        if (fpList[0].get('aHour') * 60 + fpList[0].get('aMin')) < slots[slotIndex + 1]:
            fpDic.update({str(slots[slotIndex] // 60) + ':' + str(slots[slotIndex] % 60) : fpList[0]})
            fpList.pop(0)
        else:
            fpDic.update({str(slots[slotIndex] // 60) + ':' + str(slots[slotIndex] % 60) : None})
        
    return fpDic

# --------------------------------------------------------------------------------------------
# MAIN PROGRAM

arrivals = main()
slots = getSlots(AAR, PAAR, rStart, rEnd)
defineType(arrivals, rStart, rEnd, margin, radius)
