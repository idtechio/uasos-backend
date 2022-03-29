DROP TABLE IF EXISTS hosts;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS hosts (
     db_hosts_id VARCHAR DEFAULT uuid_generate_v1mc() NOT NULL PRIMARY KEY	
    ,fnc_ts_registered VARCHAR(13)
    ,fnc_status VARCHAR
	,fnc_score INTEGER
    ,name VARCHAR
    ,country VARCHAR
    ,phone_num VARCHAR
    ,email VARCHAR
    ,city VARCHAR
    ,children_allowed VARCHAR
    ,pet_allowed VARCHAR
    ,handicapped_allowed VARCHAR
    ,num_people INTEGER
    ,period INTEGER
    ,pietro INTEGER
    ,listing_country VARCHAR
    ,shelter_type VARCHAR
    ,beds INTEGER
    ,acceptable_group_relations VARCHAR
    ,ok_for_pregnant VARCHAR
    ,ok_for_disabilities VARCHAR
    ,ok_for_animals VARCHAR
    ,ok_for_elderly VARCHAR
    ,ok_for_any_nationality VARCHAR
    ,duration_category VARCHAR
);

SELECT * FROM hosts;
