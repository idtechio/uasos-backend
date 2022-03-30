DROP TABLE IF EXISTS matches;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS matches (
     db_matches_id VARCHAR DEFAULT uuid_generate_v1mc() NOT NULL PRIMARY KEY
    ,db_ts_matched VARCHAR(13) DEFAULT FLOOR(EXTRACT(epoch FROM NOW())*1000)
    ,fnc_status VARCHAR
    ,fnc_hosts_id VARCHAR NOT NULL
    ,fnc_guests_id VARCHAR NOT NULL
    ,fnc_host_status VARCHAR
    ,fnc_guest_status VARCHAR
);

-- ALTER TABLE matches ADD CONSTRAINT fk_matches_guests_id FOREIGN KEY (fnc_guests_id) REFERENCES guests (db_guests_id);
-- ALTER TABLE matches ADD CONSTRAINT fk_matches_hosts_id FOREIGN KEY (fnc_hosts_id) REFERENCES hosts (db_hosts_id);
