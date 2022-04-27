DROP TABLE IF EXISTS accounts;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS accounts (
     db_accounts_id VARCHAR DEFAULT uuid_generate_v1mc() NOT NULL PRIMARY KEY
    ,db_ts_registered VARCHAR(13) DEFAULT FLOOR(EXTRACT(epoch FROM NOW())*1000)
    ,fnc_status VARCHAR
    ,uid VARCHAR
    ,name VARCHAR
    ,email VARCHAR
    ,phone_num VARCHAR
    ,fnc_email_status VARCHAR
    ,fnc_msisdn_status VARCHAR
    ,preferred_lang VARCHAR
    ,sms_notification VARCHAR
    ,identity_verified VARCHAR
);

CREATE UNIQUE INDEX accounts_uid_uindex
    on accounts (uid);
