DROP TABLE IF EXISTS guests;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS guests (
     db_guests_id VARCHAR DEFAULT uuid_generate_v1mc() NOT NULL PRIMARY KEY	
    ,db_ts_registered VARCHAR(13) DEFAULT FLOOR(EXTRACT(epoch FROM NOW())*1000)
    ,fnc_accounts_id VARCHAR NOT NULL
    ,fnc_status VARCHAR
    ,name VARCHAR
    ,country VARCHAR
    ,phone_num VARCHAR
    ,email VARCHAR
    ,city VARCHAR
    ,acceptable_shelter_types VARCHAR
    ,beds INTEGER
    ,group_relation VARCHAR
    ,is_pregnant VARCHAR
    ,is_with_disability VARCHAR
    ,is_with_animal VARCHAR
    ,is_with_elderly VARCHAR
    ,is_ukrainian_nationality VARCHAR
    ,duration_category VARCHAR
);
