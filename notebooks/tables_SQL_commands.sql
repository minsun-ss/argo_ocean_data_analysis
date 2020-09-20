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
