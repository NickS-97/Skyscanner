# Purpose: 1. Scan the json data feed from the raspberry pi piaware software
# 2. Reformat the json as an dataframe 
# 3. Use the dataframe to begin populating the flyvegas database tables


def scanner(db_user, db_database, db_host, db_password):

    import json
    import pandas as pd
    import datetime
    import numpy as np
    import mysql.connector
    from mysql.connector.constants import ClientFlag
    import urllib.request, json 

    # Open json file that has flights saved TODO delete this when hooked up to pi
    #f = open('D:\Learning\Skyscanner\\test_data\sky_test6.json')

    #return json data as a dictionary
    #data = json.load(f)

    # Read in piaware 1090 dump feed (json file) and decode the json file
    with urllib.request.urlopen("http://192.168.0.79/dump1090-fa/data/aircraft.json") as url:
        data = json.loads(url.read().decode())


    # Create a new dataframe for the json date - easier to import data from a dataframe into database rather than from json files
    df = pd.DataFrame(columns = ['alt_baro', 'alt_geom', 'baro_rate', 'category', 'emergency', 'flight',
    'geom_rate', 'gs', 'gva', 'hex', 'lat', 'lon', 'messages','nac_p',
    'nac_v', 'nav_altitude_mcp', 'nav_heading', 'nav_modes', 'nav_qnh', 'nic',
    'nic_baro', 'rc', 'rssi', 'sda', 'seen', 'seen_pos', 'sil', 'sil_type', 'squawk', 'track', 'version']
    )

    # Reformat the json data as a dataframe. 
    for x in data['aircraft']:
        df = df.append(x, ignore_index = True)

    # Change nan values to -999.9 for mysql purposes - we will be able to easily identify these in the database and can remove
    df = df.replace({np.nan: -999.9})

    # Create empty lists for our insert calls
    insert1 = [] #aircraft_info
    insert2 = [] #flight_info
    insert3 = [] #scanned_flights
    insert4 = [] #aircraft_info_nc (no callsign)
    insert5 = [] #scanned_flights_nc (no callsign)

    # loop through the dataframe to grab the necessary data for each table 
    for index, row in df.iterrows():
        
        #create flight timestamps based on the time of webscraping (create local timestamp PST)
        now = datetime.datetime.now()
        flight_timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

        #create UTC timestamp
        now_utc = datetime.datetime.utcnow()
        flight_timestamp_utc = now_utc.strftime('%Y-%m-%d %H:%M:%S')

        # check if there is a callsign (comes in as 'flight') for the scanned plane. If yes, populate lists for insert calls
        if isinstance(row['flight'], str):

            
            insert1.append((row['hex'],))

            # Create callsign date which will be used as a PK in flight_info table
            callsign_date = str(row['flight']).strip() + "_" + flight_timestamp

            insert2.append((callsign_date, str(row['flight']).strip(), datetime.datetime.now()))    

            insert3.append((flight_timestamp, row['hex'], float(row['alt_baro']), float(row['alt_geom']), float(row['baro_rate']), str(row['category']),
                        str(row['emergency']), str(row['flight']), float(row['geom_rate']), float(row['gs']), float(row['gva']), float(row['lat']), float(row['lon']),
                        int(row['messages']), float(row['nac_p']), float(row['nac_v']), float(row['nav_altitude_mcp']), float(row['nav_heading']),
                        float(row['nav_qnh']), float(row['nic']), float(row['nic_baro']), float(row['rc']), float(row['rssi']),
                        float(row['sda']), float(row['seen']), float(row['seen_pos']), float(row['sil']), str(row['sil_type']), str(row['squawk']),
                        float(row['track']), int(row['version']), callsign_date, flight_timestamp_utc))

        #else function is used for insert statements that will populate the "no-callsign" (NC) tables
        else:
            insert4.append((row['hex'],))   
        
            insert5.append((flight_timestamp, row['hex'], float(row['alt_baro']), float(row['alt_geom']), float(row['baro_rate']), str(row['category']),
                        str(row['emergency']), str(row['flight']), float(row['geom_rate']), float(row['gs']), float(row['gva']), float(row['lat']), float(row['lon']),
                        int(row['messages']), float(row['nac_p']), float(row['nac_v']), float(row['nav_altitude_mcp']), float(row['nav_heading']),
                        float(row['nav_qnh']), float(row['nic']), float(row['nic_baro']), float(row['rc']), float(row['rssi']),
                        float(row['sda']), float(row['seen']), float(row['seen_pos']), float(row['sil']), str(row['sil_type']), str(row['squawk']),
                        float(row['track']), int(row['version']), flight_timestamp_utc))


    # connect to cloud database using proper credentials including SSL
    #connection = mysql.connector.connect(user = db_user, database = db_database, host = db_host, password = db_password)
    connection = mysql.connector.connect(user = db_user, database = db_database, host = db_host, password = db_password, 
                                        client_flags = [ClientFlag.SSL], ssl_ca = 'D:\Learning\Skyscanner\program_scripts\modules\Connection\ca.pem',
                                        ssl_cert = 'D:\Learning\Skyscanner\program_scripts\modules\Connection\client-cert.pem', 
                                        ssl_key = 'D:\Learning\Skyscanner\program_scripts\modules\Connection\client-key.pem' )
    mycursor = connection.cursor()

    # Insert hex code into aircraft info table first
    sql_insert1 = "INSERT IGNORE INTO aircraft_info(hex) VALUES (%s)"
    mycursor.executemany(sql_insert1, insert1)
    connection.commit()

    # Insert callsign and date into detailed flight info
    sql_insert2 = "INSERT INTO flight_info (callsign_date, callsign, date) VALUES (%s, %s, %s)"
    mycursor.executemany(sql_insert2, insert2)
    connection.commit()

    # Insert scanned flights with a callsign into scanned flights table
    sql_insert3 = ("""INSERT INTO scanned_flights (flight_timestamp, hex, alt_baro, alt_geom, baro_rate, category,
                                                emergency, flight, geom_rate, gs, gva, lat, lon,
                                                messages, nac_p, nac_v, nav_altitude_mcp, nav_heading,
                                                nav_qnh, nic, nic_baro, rc, rssi, sda,
                                                seen, seen_pos, sil, sil_type, squawk, track, version, callsign_date, flight_timestamp_utc) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""")
    mycursor.executemany(sql_insert3, insert3)
    connection.commit()

    # Insert flights without a callsign into aircraft_info and scanned flights tables
    sql_insert4 = "INSERT IGNORE INTO aircraft_info_nc(hex) VALUES (%s)"
    mycursor.executemany(sql_insert4, insert4)
    connection.commit()

    sql_insert5 = ("""INSERT INTO scanned_flights_nc (flight_timestamp, hex, alt_baro, alt_geom, baro_rate, category,
                                                emergency, flight, geom_rate, gs, gva, lat, lon,
                                                messages, nac_p, nac_v, nav_altitude_mcp, nav_heading,
                                                nav_qnh, nic, nic_baro, rc, rssi, sda,
                                                seen, seen_pos, sil, sil_type, squawk, track, version, flight_timestamp_utc) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""")
    mycursor.executemany(sql_insert5, insert5)
    connection.commit()

    return (insert3)

