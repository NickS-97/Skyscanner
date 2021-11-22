# Purpose: Make calls to the Airport-Info API to populate the airport_info table

def airport_info(db_user, db_database, db_host, db_password, api_host, api_key):
    import json
    import pandas as pd
    import datetime
    import mysql.connector
    import numpy as np
    import requests
    import re

    # set up api information
    url = "https://airport-info.p.rapidapi.com/airport"
    headers = {
        'x-rapidapi-host': api_host,
        'x-rapidapi-key': api_key
        }

    # connect to database
    connection = mysql.connector.connect(user = db_user, database = db_database, host = db_host, password = db_password)
    mycursor = connection.cursor()

    # select the rows that have not been run through the api
    sql_select1 = """SELECT airport_iata
                    FROM airport_info 
                    WHERE api_scan = 0"""

    mycursor.execute(sql_select1)
    query_result = mycursor.fetchall()

    # create an empty update list to do an execute many statement
    update = []

    # loop through query result
    for x in query_result:
        
        try:
            # create querystring for api call
            querystring = {"iata": x[0]}
            response = requests.request("GET", url, headers=headers, params=querystring)
            result = response.json()

            # update api_scan column
            api_scan = 1
            
            # populate list with items from api call
            update.extend([[result['name'], result['location'], result['street_number'], result['city'], result['county'], result['state'], result['country_iso'], result['postal_code'], 
                            result['latitude'], result['longitude'], result['uct'], result['icao'], api_scan, x[0]]])
        
        except:
            pass

    try:
        # insert the airport information in the database
        sql_update = """UPDATE airport_info 
                    SET airport_name = %s, airport_location = %s, street_number = %s, city = %s,
                        county = %s, airport_state = %s, country_iso = %s,
                        postal_code = %s, latitude = %s, longitude = %s, uct = %s, airport_icao = %s, api_scan = %s 
                    WHERE airport_iata = %s"""

        mycursor.executemany(sql_update, update)
        connection.commit()
    except:
        pass