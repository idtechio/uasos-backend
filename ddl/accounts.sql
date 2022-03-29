DROP TABLE IF EXISTS accounts;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS accounts (
     db_accounts_id VARCHAR DEFAULT uuid_generate_v1mc() NOT NULL PRIMARY KEY
    ,fnc_ts_registered VARCHAR(13) DEFAULT FLOOR(EXTRACT(epoch FROM NOW())*1000)
    ,fnc_status VARCHAR
    ,uid VARCHAR
    ,name VARCHAR
    ,email VARCHAR
    ,phone_num VARCHAR
    ,is_email_verified VARCHAR
    ,is_phone_verified VARCHAR
    ,preferred_lang VARCHAR
);

SELECT * FROM accounts;

CREATE UNIQUE INDEX accounts_uid_uindex
    on accounts (uid);