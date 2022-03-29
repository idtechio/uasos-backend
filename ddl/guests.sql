DROP TABLE IF EXISTS guests;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS guests (
     db_guests_id VARCHAR DEFAULT uuid_generate_v1mc() NOT NULL PRIMARY KEY	
    ,fnc_ts_registered VARCHAR(13)
    ,fnc_status VARCHAR
	,fnc_score INTEGER
    ,name VARCHAR
    ,country VARCHAR
    ,phone_num VARCHAR
    ,email VARCHAR
    ,city VARCHAR
    ,is_children VARCHAR
    ,is_pet VARCHAR
    ,is_handicapped VARCHAR
    ,num_people INTEGER
    ,period INTEGER
    ,listing_country VARCHAR
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

SELECT * FROM guests;
