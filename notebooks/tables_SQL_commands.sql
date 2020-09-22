--- Create tables and index them in the database. ---

-- Create ocean_data table --
CREATE TABLE OCEAN_DATA (
    id SERIAL PRIMARY KEY,
    data_date timestamp,
    floatid varchar(100),
    latitude decimal,
    longitude decimal,
    depth varchar(100),
    temperature decimal,
    salinity decimal,
    data_source varchar(100)
);

-- Create B-Tree index on latitude and longitude. Also index on data_source and date. --
CREATE INDEX idx_position
ON OCEAN_DATA (latitude, longitude);

CREATE INDEX idx_source
ON OCEAN_DATA (data_source);

CREATE INDEX idx_date
ON OCEAN_DATA (data_date);

-- If needed: change column type
ALTER TABLE ocean_data
ALTER COLUMN depth TYPE DECIMAL;

-- Fish data table
CREATE TABLE fish_data (
id SERIAL NOT NULL,
date date NOT NULL,
station int,
longitude decimal (30,10),
latitude decimal (30,10),
depth real,
fish_type varchar(50),
fish_count real,
region varchar(20),
PRIMARY KEY (id)
);

-- gtspp intermediary table
CREATE TABLE gtspp (
id SERIAL NOT NULL,
longitude decimal (30,10),
latitude decimal (30,10),
position_quality int,
station_id int,
measure_time timestamp,
measure_time_quality int,
salinity real,
salinity_quality int,
depth real,
depth_quality int,
temperature real,
temperature_quality int,
PRIMARY KEY (id)
);


-- Select sample data to map points --
SELECT DISTINCT(ROUND(latitude, 1), ROUND(longitude, 1))
FROM (SELECT * from ocean_data TABLESAMPLE SYSTEM (10)) as sample;

-- Get size of tables in db --
SELECT nspname || '.' || relname AS "relation",
pg_size_pretty(pg_total_relation_size(C.oid)) AS "total_size"
FROM pg_class C
LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
WHERE nspname NOT IN ('pg_catalog', 'information_schema')
AND C.relkind <> 'i'
AND nspname !~ '^pg_toast'
ORDER BY pg_total_relation_size(C.oid) DESC
LIMIT 5;