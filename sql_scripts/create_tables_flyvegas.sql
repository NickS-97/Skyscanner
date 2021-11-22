-- Script to drop and create all the tables in the flyvegas database

-- Tell mariadb which db to use
USE flyvegas;


-- Drop all tables if they exist (clear db). Based on my understanding maria db
-- does not let you do a cascade drop, so you have to drop all tables individually
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS scanned_flights;
DROP TABLE IF EXISTS aircraft_info;
DROP TABLE IF EXISTS flight_info; 
DROP TABLE IF EXISTS general_flight_info;
DROP TABLE IF EXISTS airport_info;
DROP TABLE IF EXISTS airline_info;
DROP TABLE IF EXISTS scanned_flights_nc;

DROP TABLE IF EXISTS aircraft_info_nc;

SET FOREIGN_KEY_CHECKS = 1;


-- Create all the tables in the db

CREATE TABLE IF NOT EXISTS scanned_flights(
	-- create columns

	flight_timestamp datetime NOT NULL,
	hex varchar(10) NOT NULL,
	alt_baro float(5),
	alt_geom float(5),
	baro_rate float(5),
	category varchar(6),
	emergency varchar(20),
	flight varchar(10),
	geom_rate float(10),
	gs float(6),
	gva float(3),
	lat float(10),
	lon float(12),
	messages int(4),
	nac_p float(4),
	nac_v float(4),
	nav_altitude_mcp float(6),
	nav_heading float(5),
	nav_modes float(6),
	nav_qnh float(6),
	nic float(5),
	nic_baro float(5),
	rc float(5),
	rssi float(6),
	sda float(5),
	seen float(5),
	seen_pos float(5),
	sil float(5),
	sil_type varchar(15),
	squawk varchar(20),
	track float(6),
	version int(2),
	-- date date,
	callsign_date varchar(50) NULL,
	flight_timestamp_utc datetime,

	-- create constraints
	CONSTRAINT pk_scanned_flights PRIMARY KEY(flight_timestamp, hex)

);


CREATE TABLE IF NOT EXISTS flight_info (
	-- create columns

	callsign_date varchar(50) NOT NULL,
	callsign varchar(10) NOT NULL,
	date date NOT NULL,
	dep_airport_iata varchar(4),
	arr_airport_iata varchar(4),
	airline_iata varchar(4),
	flight_number varchar(10),
	dep_sch_time_local varchar(30),
	dep_act_time_local varchar(30),
	dep_sch_time_utc varchar(30),
	dep_act_time_utc varchar(30),
	arr_sch_time_local varchar(30),
	arr_act_time_local varchar(30),
	arr_sch_time_utc varchar(30),
	arr_act_time_utc varchar(30),
	api_scan bit DEFAULT 0,

	-- create key constraints


	CONSTRAINT pk_flight_info PRIMARY KEY (callsign_date)
);

ALTER TABLE scanned_flights ADD FOREIGN KEY (callsign_date) REFERENCES flight_info (callsign_date);

CREATE TABLE IF NOT EXISTS airline_info(
	-- create columns
	airline_icao varchar(5) NOT NULL,
	airline_iata varchar(5),
	airline_name varchar(40),
	api_scan bit DEFAULT 0,

	-- create key constraints
	CONSTRAINT pk_airline_info PRIMARY KEY (airline_iata)
);

ALTER TABLE flight_info ADD FOREIGN KEY (airline_iata) REFERENCES airline_info(airline_iata);

CREATE TABLE IF NOT EXISTS airport_info(
	-- create columns
	airport_iata varchar(5) NOT NULL,
	airport_icao varchar(5),
	airport_name varchar(100),
	airport_location varchar(200),
	street_number varchar(10),
	city varchar(50),
	county varchar(60),
	airport_state varchar(30),
	country_iso varchar(5),
	country varchar(50),
	postal_code varchar(15),
	latitude float(10),
	longitude float(12),
	uct int(4),
	api_scan bit DEFAULT 0,

	-- create constraints
	CONSTRAINT pk_airport_info PRIMARY KEY (airport_iata)
);

ALTER TABLE flight_info ADD FOREIGN KEY (dep_airport_iata) REFERENCES airport_info(airport_iata);
ALTER TABLE flight_info ADD FOREIGN KEY (arr_airport_iata) REFERENCES airport_info(airport_iata);


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
	model_code varchar(30),
	num_seats int(5),
	rollout_date varchar(30),
	first_flight_date varchar(30),
	delivery_date varchar(30),
	registration_date varchar(30),
	type_name varchar(40),
	num_engines int(2),
	engine_type varchar(10),
	is_freighter bit,
	api_scan bit DEFAULT 0,

	-- create constraints
	CONSTRAINT pk_aircraft_info PRIMARY KEY (hex)
);

ALTER TABLE scanned_flights ADD FOREIGN KEY (hex) REFERENCES aircraft_info(hex);

CREATE TABLE IF NOT EXISTS scanned_flights_nc(
	-- create columns

	flight_timestamp datetime NOT NULL,
	hex varchar(10) NOT NULL,
	alt_baro float(5),
	alt_geom float(5),
	baro_rate float(5),
	category varchar(6),
	emergency varchar(20),
	flight varchar(10),
	geom_rate float(10),
	gs float(6),
	gva float(3),
	lat float(10),
	lon float(12),
	messages int(4),
	nac_p float(4),
	nac_v float(4),
	nav_altitude_mcp float(6),
	nav_heading float(5),
	nav_modes float(6),
	nav_qnh float(6),
	nic float(5),
	nic_baro float(5),
	rc float(5),
	rssi float(6),
	sda float(5),
	seen float(5),
	seen_pos float(5),
	sil float(5),
	sil_type varchar(15),
	squawk varchar(20),
	track float(6),
	version int(2),
	flight_timestamp_utc datetime,

	-- create constraints
	CONSTRAINT pk_scanned_flights_nc PRIMARY KEY(flight_timestamp, hex)

);

CREATE TABLE IF NOT EXISTS aircraft_info_nc(
	-- create columns
	hex varchar(10) NOT NULL,
	reg varchar(8),
	-- use bit datatype to represent a boolean value (1 = yes, 0 = no)
	active bit,
	serial varchar(6),
	airline_name varchar(40), 
	iata_short varchar(5),
	iata_long varchar(10),
	model varchar(10),
	model_code varchar(30),
	numseats int(5),
	rollout_date varchar(30),
	first_flight_date varchar(30),
	delivery_date varchar(30),
	registration_date varchar(30),
	type_name varchar(40),
	num_engines int(2),
	engine_type varchar(10),
	is_freighter bit,
	api_scan bit DEFAULT 0, 

	-- create constraints
	CONSTRAINT pk_aircraft_info_nc PRIMARY KEY (hex)
);

ALTER TABLE scanned_flights_nc ADD FOREIGN KEY (hex) REFERENCES aircraft_info_nc(hex);