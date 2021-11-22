-- Script to drop and create all the tables in the flyvegas database

-- Tell mariadb which db to use
USE flyvegas;


-- Drop all tables if they exist (clear db). Based on my understanding maria db
-- does not let you do a cascade drop, so you have to drop all tables individually
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS scanned_flights;
DROP TABLE IF EXISTS airport_info;
DROP TABLE IF EXISTS detailed_flight_info; 
DROP TABLE IF EXISTS general_flight_info;
DROP TABLE IF EXISTS airport_info;
DROP TABLE IF EXISTS airline_info;

SET FOREIGN_KEY_CHECKS = 1;


-- Create all the tables in the db

CREATE TABLE IF NOT EXISTS scanned_flights(
	-- create columns

	flight_timestamp timestamp NOT NULL,
	hex varchar(10) NOT NULL,
	alt_baro int(5),
	alt_geom int(5),
	baro_rate int(5),
	category varchar(4),
	emergency varchar(20),
	flight varchar(10),
	geom_rate float(7),
	gs float(6),
	gva int(2),
	lat float(10),
	lon float(12),
	messages int(4),
	nac_p int(3),
	nac_v int(3),
	nav_altitude_mcp int(5),
	nav_heading float(5),
	nav_modes float(6),
	nav_qnh float(6),
	nic int(5),
	nic_baro int(5),
	rc int(5),
	rssi float(6),
	sda int(5),
	seen float(5),
	seen_pos float(5),
	sil int(5),
	sil_type varchar(15),
	squawk varchar(20),
	track float(6),
	version int(2),
	date date,
	callsign_date varchar(50),

	-- create constraints
	CONSTRAINT pk_scanned_flights PRIMARY KEY(flight_timestamp, hex)

);


CREATE TABLE IF NOT EXISTS detailed_flight_info (
	-- create columns

	callsign_date varchar(50) NOT NULL,
	callsign varchar(10) NOT NULL,
	date date NOT NULL,
	flight_number varchar(10),
	dep_sch_time_local timestamp,
	dep_act_time_local timestamp,
	dep_sch_time_utc timestamp,
	dep_act_time_utc timestamp,
	arr_sch_time_local timestamp,
	arr_act_time_local timestamp,
	arr_sch_time_utc timestamp,
	arr_act_time_utc timestamp,

	-- create key constraints


	CONSTRAINT pk_detailed_flight_info PRIMARY KEY (callsign_date)
);

ALTER TABLE scanned_flights ADD FOREIGN KEY (callsign_date) REFERENCES detailed_flight_info (callsign_date);

CREATE TABLE IF NOT EXISTS general_flight_info(
	-- create columns

	callsign varchar(10) NOT NULL,
	dep_airport_iata varchar(5),
	arr_airport_iata varchar(5),
	flight_route varchar(10),
	airline_iata varchar(5),

	-- note: route is departure airport + arrival airport

	-- create key constraints
	
	CONSTRAINT pk_general_flight_info PRIMARY KEY (callsign)
);

ALTER TABLE detailed_flight_info ADD FOREIGN KEY (callsign) REFERENCES general_flight_info(callsign);

CREATE TABLE IF NOT EXISTS airline_info(
	-- create columns
	airline_iata varchar(5) NOT NULL,
	airline_name varchar(40) NOT NULL,

	-- create key constraints
	CONSTRAINT pk_airline_info PRIMARY KEY (airline_iata)
);

ALTER TABLE general_flight_info ADD FOREIGN KEY (airline_iata) REFERENCES airline_info(airline_iata);

CREATE TABLE IF NOT EXISTS airport_info(
	-- create columns
	airport_iata varchar(5) NOT NULL,
	airport_name varchar(100),
	airport_location varchar(200),
	street_number varchar(10),
	city varchar(50),
	county varchar(60),
	airport_state varchar(30),
	county_iso varchar(5),
	country varchar(50),
	postal_code varchar(15),
	latitude float(10),
	longitude float(12),
	uct int(4),

	-- create constraints
	CONSTRAINT pk_airport_info PRIMARY KEY (airport_iata)
);

ALTER TABLE general_flight_info ADD FOREIGN KEY (dep_airport_iata) REFERENCES airport_info(airport_iata);
ALTER TABLE general_flight_info ADD FOREIGN KEY (arr_airport_iata) REFERENCES airport_info(airport_iata);


CREATE TABLE IF NOT EXISTS aircraft_info(
	-- create columns
	hex varchar(10) NOT NULL,
	reg varchar(8),
	-- use bit datatype to represent a boolean value (1 = yes, 0 = no)
	active bit,
	serial varchar(6),
	-- name below is unnecessary as we have name in the airline table. While I understand it is redundant data I am fine with 
	-- this redundancy as it will make data collection and EDA easier 
	airline_name varchar(40),
	iata_short varchar(5),
	iata_long varchar(10),
	model varchar(10),
	model_code varchar(15),
	first_flight_date date,
	delivery_date date,
	registration_date date,
	type_name varchar(40),
	num_engines int(2),
	engine_type varchar(10),
	is_freighter bit,

	-- create constraints
	CONSTRAINT pk_aircraft_info PRIMARY KEY (hex)
);

ALTER TABLE scanned_flights ADD FOREIGN KEY (hex) REFERENCES aircraft_info(hex);