# Purpose: Make calls to the AeroDataBox API to populate the airport_info table

def aircraft_info(db_user, db_database, db_host, db_password, api_host, api_key):
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
    url = "https://aerodatabox.p.rapidapi.com/aircrafts/icao24/"
    headers = {
        'x-rapidapi-host': api_host,
        'x-rapidapi-key': api_key
        }

    # make a sql call to get hex codes from the aircraft_info and aicraft_info_nc tables

    sql_select1  = """SELECT hex FROM aircraft_info WHERE api_scan = 0"""
    
    mycursor.execute(sql_select1)
    query_result = mycursor.fetchall()

    # get results from aircraft_info_nc table
    sql_select2  = """SELECT hex FROM aircraft_info_nc WHERE api_scan = 0"""

    mycursor.execute(sql_select2)
    query_result2 = mycursor.fetchall()

    # create an empty update list to do an execute many statement
    update = []
    update2 = [] # for nc table

    # loop through query result
    for x in query_result:
        
        try:
            # create search_url for api call
            search_url = url + x[0]
            response = requests.request("GET", url, headers=headers)
            result = response.json()

            # grab data
            reg = result['reg']
            active = (1 if result['active'] == 'true' else 0)
            serial = result['serial']
            airline = result['airlineName']
            iata_short = result['iataCodeShort']
            iata_long = result['iataCodeLong']
            model = result['model']
            model_code = result['modelCode']
            first_flight_date = result['firstFlightDate']
            delivery_date = result['deliveryDate']
            registration_date = result['registrationDate']
            type_name = result['typeName']
            num_engines = result['numEngines']
            engine_type = result['engineType']
            is_freighter = (1 if result['isFreighter'] == 'true' else 0)

            # update api_scan column
            api_scan = 1

            update.extend([[reg, active, serial, airline, iata_short, iata_long, model, model_code, first_flight_date,
                            delivery_date, registration_date, type_name, num_engines, engine_type, is_freighter, api_scan, x[0]]])

        except: pass

        # loop through query result
    for x in query_result2:
        
        try:
            # create search_url for api call
            search_url = url + x[0]
            response = requests.request("GET", url, headers=headers)
            result = response.json()

            # grab data
            reg = result['reg']
            active = (1 if result['active'] == 'true' else 0)
            serial = result['serial']
            airline = result['airlineName']
            iata_short = result['iataCodeShort']
            iata_long = result['iataCodeLong']
            model = result['model']
            model_code = result['modelCode']
            first_flight_date = result['firstFlightDate']
            delivery_date = result['deliveryDate']
            registration_date = result['registrationDate']
            type_name = result['typeName']
            num_engines = result['numEngines']
            engine_type = result['engineType']
            is_freighter = (1 if result['isFreighter'] == 'true' else 0)

            # update api_scan column
            api_scan = 1

            update2.extend([[reg, active, serial, airline, iata_short, iata_long, model, model_code, first_flight_date,
                            delivery_date, registration_date, type_name, num_engines, engine_type, is_freighter, api_scan, x[0]]])

        except: pass

    # create sql update scripts for both aircraft_info and aircraft_info_nc tables

    try:
        sql_update1 = """UPDATE aircraft_info 
                        SET reg = %s, active = %s, serial = %s, airline_name = %s, iata_short = %s, iata_long = %s, model = %s,
                            model_code = %s, first_flight_date = %s, delivery_date = %s, registration_date = %s, type_name = %s,
                            num_engines = %s, engine_type = %s, is_freighter = %s, api_scan = %s
                        WHERE hex = %s"""

        mycursor.executemany(sql_update1, update)
        connection.commit()
    
    except:
        pass

    try:
        sql_update2 = """UPDATE aircraft_info_nc
                        SET reg = %s, active = %s, serial = %s, airline_name = %s, iata_short = %s, iata_long = %s, model = %s,
                            model_code = %s, first_flight_date = %s, delivery_date = %s, registration_date = %s, type_name = %s,
                            num_engines = %s, engine_type = %s, is_freighter = %s, api_scan = %s
                        WHERE hex = %s"""

        mycursor.executemany(sql_update2, update2)
        connection.commit()
    except:
        pass

  

