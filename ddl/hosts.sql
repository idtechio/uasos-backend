DROP TABLE IF EXISTS hosts;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS hosts (
     db_hosts_id VARCHAR DEFAULT uuid_generate_v1mc() NOT NULL PRIMARY KEY	
    ,db_ts_registered VARCHAR(13) DEFAULT FLOOR(EXTRACT(epoch FROM NOW())*1000)
    ,fnc_accounts_id VARCHAR
    ,fnc_status VARCHAR
    ,name VARCHAR
    ,country VARCHAR
    ,phone_num VARCHAR
    ,email VARCHAR
    ,city VARCHAR
    ,closest_city VARCHAR
    ,zipcode VARCHAR
    ,street VARCHAR
    ,building_no VARCHAR
    ,appartment_no VARCHAR
    ,shelter_type VARCHAR
    ,host_type VARCHAR
    ,beds INTEGER
    ,acceptable_group_relations VARCHAR
    ,ok_for_pregnant VARCHAR
    ,ok_for_disabilities VARCHAR
    ,ok_for_animals VARCHAR
    ,ok_for_elderly VARCHAR
    ,ok_for_any_nationality VARCHAR
    ,duration_category VARCHAR
    ,transport_included VARCHAR
    ,can_be_verified VARCHAR
);
