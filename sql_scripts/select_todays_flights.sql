--SQL statements to select data from the database to search in API

--Statement to select the callsigns and the flight date from the database
SELECT detailed_flight_info.callsign, DATE(scanned_flights.flight_timestamp) 
FROM detailed_flight_info 
INNER JOIN scanned_flights ON detailed_flight_info.callsign_date = scanned_flights.callsign_date
WHERE DATE(scanned_flights.flight_timestamp) = DATE(CURRENT_TIMESTAMP());