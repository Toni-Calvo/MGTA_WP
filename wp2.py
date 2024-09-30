from Hfile import main


distanceAirport = {'UUEE', 'LROP', 'DAAG', 'LFRI', 'ENGM', 'LIML', 'EDQA', 'ESGG', 'EDDF', 'EVRA', 'GCLP', 'EDDV', 'ELLX', 'LHBP', 'EDDM', 'EKCH', 'LEMD', 'EDDH', 'EIDW', 'LFPO', 'LSGG', 'EDDT', 'LESO', 'LEST', 'EHAM', 'LEPA', 'LEMH', 'LEAL', 'LEBB', 'LPPT', 'EGKK', 'LECO', 'LEMG', 'LEZL', 'EBBR', 'LEIB', 'LIMC', 'LIRF', 'LLBG', 'LEGR', 'LEVX', 'LEAS', 'LFPG', 'SBGR', 'LSZH', 'LGAV', 'GCXO', 'EGBB', 'GMMN', 'LRTR', 'LFSB', 'EDDB', 'KEWR', 'EGCC', 'EGLL', 'LKPR', 'EBLG', 'LTFJ', 'LOWW', 'LPPR', 'GCTS', 'KJFK', 'EPWA', 'LFLL', 'LIPZ', 'EGPH', 'LFML', 'EHEH', 'LFRN', 'LIRN', 'SAEZ', 'GCRR', 'ESSA', 'EBOS', 'EDDP', 'EDDK', 'EDDL', 'LIBD', 'EDDS', 'LEVD', 'EGSS', 'LICJ', 'LIME', 'OTHH', 'EHRD', 'LFOB', 'EGGP', 'LEVC', 'EPMO', 'LFBD', 'LEAM', 'LTBA', 'LRCL', 'LIMF', 'SKBO', 'LFMN', 'HECA', 'LBSF', 'OMDB', 'EBAW', 'GMFF', 'LIRQ', 'LEXJ', 'EGNT', 'EGGW', 'EGGD', 'EGNM', 'LFRS', 'LEJR', 'GMMX', 'LIRP', 'LIPE', 'GMMW', 'DTTA', 'LIPH', 'LELN', 'EFHK', 'LEZG', 'LFLI', 'GCFV', 'GMTT'}


def createSlots(min, hStart, hEnd):
    """Creates slots for the given time in minutes."""
    slots = []
    for i in range(hStart, hEnd):
        for j in range(0, 60, min):
            slots.append((i * 60) + j)
            
            
def defineGDP(flightPlans, minStart, minEnd, margin, radius):
    """Defines a GDP and return the list of flights affected."""
    for flightPlan in flightPlans:
        arrival = flightPlan.get('aHour') * 60 + flightPlan.get('aMin')
        if minStart <= arrival <= minEnd:
            if distanceAirport.get(flightPlan.get('departure_airport')) <= radius:
                flightPlan.update({'GDP' : True})
                