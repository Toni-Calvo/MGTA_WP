def parse_allft_plus_file(filepath):
    flights_data = []  # List to hold all flights data
    with open(filepath, 'r') as file:
        next(file)  # Skip the first line (version of the allft file)
        for line in file:
            flight_details = line.strip().split(';')
            waypoints = flight_details[85].split(" ")
            flight_dict = {
                'departure_airport': flight_details[0],
                'arrival_airport': flight_details[1],
                'flight_number': flight_details[2],
                'airline_code': flight_details[3],
                'aircraft_type': flight_details[4],
                'scheduled_departure': (waypoints[0].split(":"))[0],  # ETD is given by first waypoint
                'scheduled_arrival': (waypoints[-1].split(":"))[0],  # ETA is given by last waypoint
                # Add more fields if necessary
            }
            flights_data.append(flight_dict)

    return flights_data
