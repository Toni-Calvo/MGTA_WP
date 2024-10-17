import numpy as np
from wp1 import main, isInECAC, getDistance, getSlots, plotSlotsArrOverTime

# --------------------------------------------------------------------------------------------
# GLOBAL VARIABLES
Hstart = 6 # h

# --------------------------------------------------------------------------------------------
# FUNCTIONS

def filterFPs(fpDic, Hstart, HnoReg):
    """Filters all the flightplans to only show the ones between Hstart and HnoReg."""
    filteredFPs = {}
    for key in fpDic:
        if fpDic.get(key) != None:
            if Hstart * 60 < (int(key.split(':')[0]) * 60 + int(key.split(':')[1])) <= (HnoReg[0] * 60 + HnoReg[1]):
                filteredFPs.update({key : fpDic.get(key)})
    
    return filteredFPs

# --------------------------------------------------------------------------------------------
# MAIN PROGRAM
