# Purpose: Make calls to the Aero Databox API to get detailed flight info for each scanned flight 

def flight_data(db_user, db_database, db_host, db_password, api_host, api_key): 
    import json
    import pandas as pd
    import datetime
    import mysql.connector
    import numpy as np
    import requests
    import re

    # connect to cloud database using proper credentials
    connection = mysql.connector.connect(user = db_user, database = db_database, host = db_host, password = db_password)
    mycursor = connection.cursor()

    # Setup Aerodata box credentials. API link: https://rapidapi.com/aerodatabox/api/aerodatabox/
    url = "https://aerodatabox.p.rapidapi.com/flights/callsign/"
    headers = {
        'x-rapidapi-host': api_host,
        'x-rapidapi-key': api_key
        }


    # Select all callsigns from the current day's scan to get the data to send to the API TODO determine best approach between the two below
    sql_select1 = """SELECT flight_info.callsign, scanned_flights.flight_timestamp_utc, scanned_flights.flight_timestamp
                     FROM flight_info 
                     INNER JOIN scanned_flights ON flight_info.callsign_date = scanned_flights.callsign_date
                     WHERE DATE(scanned_flights.flight_timestamp) = DATE(CURRENT_TIMESTAMP())"""

    # Alternative - select first x number of scans that do not have detailed info. This may be easier to comply with API limits rather than scan everything from that day.
    # check departure airport columns to identy rows that have not been run through the api
    # sql_select1 = """SELECT flight_info.callsign, scanned_flights.flight_timestamp_utc, scanned_flights.flight_timestamp
    #                  FROM flight_info 
    #                  INNER JOIN scanned_flights ON flight_info.callsign_date = scanned_flights.callsign_date
    #                  WHERE flight_info.api_scan = 0
    #                  LIMIT 200"""

    #execute query
    mycursor.execute(sql_select1)
    query_result = mycursor.fetchall()

    #create empty lists that will be used for sql updates and imports further down
    update = [] #to update the flight_info table
    insert1 = [] #for airport_iata
    insert2 = [] #for airline_icao

    for x in query_result:
        #concatenate data for the api query url using a search date of the scan date for each isntance
        search_url = url + str(x[0]).lower() + "/" + datetime.datetime.date(x[1])
        response = requests.request("GET", search_url, headers = headers)
        results = response.json()

        # grab the timestamps for future use
        scanned_flight_utc = x[1]
        scanned_flight_local = x[2]
        
        
        # need to loop through results to find the correct flight to match the scanned time - see if scanned time is between departure and arrival
        # reason for this is because the same callsign could pertain to multiple flights in one day (i.e. SWA172 lands in LAS at 10am and departs at 2pm)
        for y in results:
            depart_time_utc = datetime.datetime.strptime(y['departure']['actualTimeUtc'], "%Y-%m-%d %H:%MZ")
            arrival_time_utc = datetime.datetime.strptime(y['arrival']['actualTimeUtc'], "%Y-%m-%d %H:%MZ")
            
            # check if our scanned flight (in utc) is between the takeoff and land times for the api result
            if scanned_flight_utc > depart_time_utc and scanned_flight_utc < arrival_time_utc:
                
                # try to capture all the data from the api result - if it does not work then pass
                try:
                    
                    # use re to get the airline iata code
                    airline_codes = re.split('(\d+)', y['callSign'])
                    airline_icao = airline_codes[0]

                    # extract all other necessary data points
                    arr_airport_iata = y['arrival']['airport']['iata']
                    dep_airport_iata = y['departure']['airport']['iata']
                    callsign = y['callSign']
                    callsign_date = y['callSign'] + "_" + str(scanned_flight_local)
                    flight_number = y['number']
                    dep_sch_time_local = y['departure']['scheduledTimeLocal']
                    dep_act_time_local = y['departure']['actualTimeLocal']
                    dep_sch_time_utc = y['departure']['scheduledTimeUtc']
                    dep_act_time_utc = y['departure']['actualTimeUtc']
                    arr_sch_time_local = y['arrival']['scheduledTimeLocal']
                    arr_act_time_local = y['arrival']['actualTimeLocal']
                    arr_sch_time_utc = y['arrival']['scheduledTimeUtc']
                    arr_act_time_utc = y['arrival']['actualTimeUtc']

                    # update the api_scan column to reflect the above
                    api_scan = 1
                    
                    # add above variables to the update list to be inserted into database
                    update.extend([[dep_airport_iata, arr_airport_iata, airline_icao, flight_number, dep_sch_time_local, dep_act_time_local, 
                    dep_sch_time_utc, dep_act_time_utc, arr_sch_time_local, arr_act_time_local, arr_sch_time_utc, arr_act_time_utc, api_scan, callsign_date]])

                    insert1.extend([(arr_airport_iata,),(dep_airport_iata,)])
                    insert2.extend([(airline_icao,)])
                    
                except:
                    pass

    try:
        #insert airport iatas. ignore if duplicate
        sql_insert1 = """INSERT IGNORE INTO airport_info(airport_iata) VALUES (%s)"""
        mycursor.executemany(sql_insert1, insert1)
        connection.commit()
    except:
        pass

    try:
        #insert airline iatas. ignore if duplicate
        sql_insert2 = """INSERT IGNORE INTO airline_info(airline_icao) VALUES (%s)"""
        mycursor.executemany(sql_insert2, insert2)
        connection.commit()
    except:
        pass

    try:
        #update the flight info with the detailed flight info from above
        sql_update = """UPDATE flight_info
                        SET dep_airport_iata = %s, arr_airport_iata = %s, airline_icao = %s, flight_number = %s, dep_sch_time_local = %s,
                            dep_act_time_local = %s, dep_sch_time_utc = %s, dep_act_time_utc = %s, arr_sch_time_local = %s, arr_act_time_local = %s,
                            arr_sch_time_utc = %s, arr_act_time_utc = %s, api_scan = %s
                        WHERE callsign_date = %s"""

        mycursor.executemany(sql_update, update)
        connection.commit()
    except:
        pass
