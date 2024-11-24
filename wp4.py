import matplotlib.pyplot as plt
from wp1 import main, getSlots, assignSlots, getAvaliableSeats
from wp2 import getWP2Results
from wp3 import filterFPs

# Redefine all data
""""distances = {
    "LEGE": 75, "LERS": 88, "LEDA": 142, "LEZG": 254, "LEPP": 352, "LESO": 401, 
    "LEVC": 303, "LEAL": 432, "LEVT": 451, "LEAB": 531, "LEGR": 681, "LEMG": 769, 
    "LEBA": 709, "LEZL": 828, "LEMD": 506, "LFMP": 157, "LFMT": 284, 
    "LFML": 506, "LFLL": 532
}"""

distances = {
    "LEZG": 254, "LESO": 401, 
    "LEVC": 303, "LEAL": 432, 
    "LEGR": 681, "LEMG": 769, 
    "LEZL": 828, "LEMD": 506, 
    "LFML": 506, "LFLL": 532
} #Km

meanTimeToAirport = 25.8 #min
meanTimeToTrainStation = 15.53
meanTimeFacturationAndSecurityCheckpoints_Airport = 90
meanTimeSecurityCheckpoints_TrainStation = 20
meanTimeToExitAirport = 38
meanTimeFromAirport_BCN = 35
meanTimeFromTrainStation_BCN = 20

""""timeByTrain = {
    "LEGE": 38, "LERS": 88, "LEDA": 58, "LEZG": 82, "LEPP": 234, "LESO": 381, 
    "LEVC": 172, "LEAL": 323, "LEVT": 296, "LEAB": 359, "LEGR": 386, "LEMG": 381, 
    "LEBA": 291, "LEZL": 347, "LEMD": 149, "LFMP": 81, "LFMT": 185, 
    "LFML": 289, "LFLL": 301
}"""

timeByTrain = {
    "LEZG": 82, "LESO": 381, 
    "LEVC": 172, "LEAL": 323,
    "LEGR": 386, "LEMG": 381, 
    "LEZL": 347, "LEMD": 149,
    "LFML": 289, "LFLL": 301
} #min

""""timeByPlane = { 
    "LEGE": 38, "LERS": 88, "LEDA": 58, "LEZG": 82, "LEPP": 234, "LESO": 381, 
    "LEVC": 172, "LEAL": 323, "LEVT": 296, "LEAB": 359, "LEGR": 386, "LEMG": 381, 
    "LEBA": 291, "LEZL": 347, "LEMD": 149, "LFMP": 81, "LFMT": 185, 
    "LFML": 289, "LFLL": 301
}"""""

timeByPlane = { 
    "LEZG": 37, "LESO": 49, 
    "LEVC": 47, "LEAL": 49,
    "LEGR": 64, "LEMG": 67, 
    "LEZL": 347, "LEMD": 51,
    "LFML": 40, "LFLL": 61
} #min


D2D_Train = {key: timeByTrain[key] + meanTimeToTrainStation + meanTimeSecurityCheckpoints_TrainStation + meanTimeFromTrainStation_BCN 
             for key in timeByTrain}

D2D_Airplane = {key: timeByPlane[key] + meanTimeToAirport + meanTimeFacturationAndSecurityCheckpoints_Airport + meanTimeToExitAirport + meanTimeFromAirport_BCN
                for key in timeByTrain}

""""CO2_Train = {
    "LEGE": 2, "LERS": 3, "LEDA": 5, "LEZG": 9, "LEPP": 15, "LESO": 18, 
    "LEVC": 7, "LEAL": 13, "LEVT": 17, "LEAB": 10, "LEGR": 22, "LEMG": 25, 
    "LEBA": 20, "LEZL": 28, "LEMD": 14, "LFMP": 10, "LFMT": 13, 
    "LFML": 20, "LFLL": 30
}"""

CO2_Train = {
    "LEZG": 9,"LESO": 18, 
    "LEVC": 7, "LEAL": 13,
    "LEGR": 22, "LEMG": 25, 
    "LEZL": 28, "LEMD": 14,
    "LFML": 20, "LFLL": 30
} #Kg/pax

""""CO2_Airplane = {
    "LEGE": 20, "LERS": 20, "LEDA": 35, "LEZG": 70, "LEPP": 80, "LESO": 100, 
    "LEVC": 50, "LEAL": 90, "LEVT": 95, "LEAB": 50, "LEGR": 110, "LEMG": 130, 
    "LEBA": 100, "LEZL": 140, "LEMD": 85, "LFMP": 50, "LFMT": 90, 
    "LFML": 100, "LFLL": 150
}"""

CO2_Airplane = {
    "LEZG": 70, "LESO": 100, 
    "LEVC": 50, "LEAL": 90,
    "LEGR": 110, "LEMG": 130, 
    "LEZL": 140, "LEMD": 85,
    "LFML": 100, "LFLL": 150
} #Kg/pax

# Sort cities by distance
ordered_cities = sorted(distances.keys(), key=lambda x: distances[x])
ordered_distances = [distances[city] for city in ordered_cities]
ordered_D2D_Train = [D2D_Train[city] for city in ordered_cities]
ordered_D2D_Airplane = [D2D_Airplane[city] for city in ordered_cities]
ordered_CO2_Train = [CO2_Train[city] for city in ordered_cities]
ordered_CO2_Airplane = [CO2_Airplane[city] for city in ordered_cities]

#Adapt the units of DTD to seconds/Km
i = 0
while i < len(ordered_D2D_Train):
    ordered_D2D_Train[i] = ordered_D2D_Train[i] * 60 / ordered_distances[i]
    i += 1
i = 0
while i < len(ordered_D2D_Airplane):
    ordered_D2D_Airplane[i] = ordered_D2D_Airplane[i] * 60 / ordered_distances[i]
    i += 1

#Adapt the units of CO2 emissions to g/ASK
i = 0
while i < len(ordered_CO2_Train):
    ordered_CO2_Train[i] = (ordered_CO2_Train[i]*1000)/ordered_distances[i]
    i += 1
i = 0
while i < len(ordered_CO2_Airplane):
    ordered_CO2_Airplane[i] = (ordered_CO2_Airplane[i]*1000)/ordered_distances[i]
    i += 1

# Plot
fig, ax1 = plt.subplots(figsize=(12, 7))

# Door-To-Door Times
ax1.set_xlabel("Distance to Barcelona (km)")
ax1.set_ylabel("D2D Time (sec/km)", color="tab:blue")
ax1.plot(ordered_distances, ordered_D2D_Train, label="Train D2D Time", color="tab:blue", marker='o')
ax1.plot(ordered_distances, ordered_D2D_Airplane, label="Airplane D2D Time", color="tab:cyan", marker='o')
ax1.tick_params(axis='y', labelcolor="tab:blue")
ax1.legend(loc="upper left")

# CO2 Emissions
ax2 = ax1.twinx()
ax2.set_ylabel("CO2 Emissions (g CO₂/ASK)", color="tab:red")
ax2.plot(ordered_distances, ordered_CO2_Train, label="Train CO2", color="tab:red", marker='x')
ax2.plot(ordered_distances, ordered_CO2_Airplane, label="Airplane CO2", color="tab:orange", marker='x')
ax2.tick_params(axis='y', labelcolor="tab:red")
ax2.legend(loc="upper right")

# Title and layout
plt.title("Comparison of D2D Times and CO2 Emissions by Distance to Barcelona")
plt.grid()
plt.tight_layout()

# Show plot
plt.show()

# --------------------------------------------------------------------------------------------
fpDic = getWP2Results()

todo = ["LEZG", "LESO", "LEVC", "LEAL","LEGR", "LEMG", "LEZL", "LEMD","LFML", "LFLL"]
airplaneDelay = {}
airplaneCO2 = {}
for aiport in todo:
    airplaneDelay[aiport] = [0, 0]
    airplaneCO2[aiport] = [0, 0]

for key in fpDic:
    if fpDic.get(key) is None:
        continue
    
    if fpDic.get(key).get('departure_airport') in todo:
        airplaneDelay[fpDic.get(key).get('departure_airport')][0] += 1
        airplaneDelay[fpDic.get(key).get('departure_airport')][1] += fpDic.get(key).get('gDelay') + fpDic.get(key).get('aDelay')
        airplaneCO2[fpDic.get(key).get('departure_airport')][0] += 1
        airplaneCO2[fpDic.get(key).get('departure_airport')][1] += fpDic.get(key).get('CO2') / getAvaliableSeats(fpDic.get(key))

for key in airplaneDelay:
    airplaneDelay[key] = airplaneDelay[key][1] / airplaneDelay[key][0]
    airplaneCO2[key] = airplaneCO2[key][1] / airplaneCO2[key][0]

newD2D_Airplane = {}
newCO2_Airplane = {}

for key in D2D_Airplane:
    newD2D_Airplane[key] = D2D_Airplane[key] + airplaneDelay[key]
    newCO2_Airplane[key] = CO2_Airplane[key] + airplaneCO2[key]

# Sort cities by distance
ordered_newD2D_Airplane = [newD2D_Airplane[city] for city in ordered_cities]
ordered_newCO2_Airplane = [newCO2_Airplane[city] for city in ordered_cities]

# Adapt the units of new DTD to seconds/Km
i = 0
while i < len(ordered_newD2D_Airplane):
    ordered_newD2D_Airplane[i] = ordered_newD2D_Airplane[i] * 60 / ordered_distances[i]
    i += 1

# Adapt the units of new CO2 emissions to g/ASK
i = 0
while i < len(ordered_newCO2_Airplane):
    ordered_newCO2_Airplane[i] = (ordered_newCO2_Airplane[i] * 1000) / ordered_distances[i]
    i += 1

# Plot updated data
fig, ax1 = plt.subplots(figsize=(12, 7))

# Door-To-Door Times
ax1.set_xlabel("Distance to Barcelona (km)")
ax1.set_ylabel("D2D Time (sec/km)", color="tab:blue")
ax1.plot(ordered_distances, ordered_D2D_Train, label="Train D2D Time", color="tab:blue", marker='o')
ax1.plot(ordered_distances, ordered_newD2D_Airplane, label="WP2 Airplane D2D Time", color="tab:green", marker='o')
ax1.tick_params(axis='y', labelcolor="tab:blue")
ax1.legend(loc="upper left")

# CO2 Emissions
ax2 = ax1.twinx()
ax2.set_ylabel("CO2 Emissions (g CO₂/ASK)", color="tab:red")
ax2.plot(ordered_distances, ordered_CO2_Train, label="Train CO2", color="tab:red", marker='x')
ax2.plot(ordered_distances, ordered_newCO2_Airplane, label="WP2 Airplane CO2", color="tab:purple", marker='x')
ax2.tick_params(axis='y', labelcolor="tab:red")
ax2.legend(loc="upper right")

# Title and layout
plt.title("Updated Comparison of D2D Times and CO2 Emissions by Distance to Barcelona")
plt.grid()
plt.tight_layout()

# Show plot
plt.show()
# --------------------------------------------------------------------------------------------

