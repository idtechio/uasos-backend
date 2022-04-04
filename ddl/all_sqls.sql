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
);

CREATE UNIQUE INDEX accounts_uid_uindex
    on accounts (uid);
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
DROP TABLE IF EXISTS hosts;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS hosts (
     db_hosts_id VARCHAR DEFAULT uuid_generate_v1mc() NOT NULL PRIMARY KEY	
    ,db_ts_registered VARCHAR(13) DEFAULT FLOOR(EXTRACT(epoch FROM NOW())*1000)
    ,fnc_accounts_id VARCHAR NOT NULL
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
);DROP TABLE IF EXISTS matches;

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
DROP VIEW IF EXISTS offers;

CREATE OR REPLACE VIEW offers AS
SELECT
    a.uid AS account_uid
    ,a.name AS host_name

    ,h.db_hosts_id AS host_id
    ,CASE
        WHEN h.fnc_status='035' THEN 'deleted'
        WHEN h.fnc_status='045' THEN 'rejected'
        WHEN h.fnc_status='065' THEN 'accepted'
        WHEN h.fnc_status='075' THEN 'being_processed'
        WHEN h.fnc_status='085' THEN 'matched'
        WHEN h.fnc_status='095' THEN 'match_accepted'
        ELSE 'default'
    END AS host_status
    ,h.city
    ,h.country
    ,a.phone_num AS phone_num
    ,a.email AS email
    ,h.closest_city
    ,h.zipcode
    ,h.street
    ,h.building_no
    ,h.appartment_no
    ,h.shelter_type
    ,h.beds
    ,h.acceptable_group_relations
    ,h.ok_for_pregnant
    ,h.ok_for_disabilities
    ,h.ok_for_animals
    ,h.ok_for_elderly
    ,h.ok_for_any_nationality
    ,h.duration_category
    ,h.transport_included
    ,h.can_be_verified

    ,CASE
        WHEN m.db_matches_id IS NULL THEN 'looking_for_match'
        WHEN m.db_matches_id IS NOT NULL AND m.fnc_status='035' THEN 'inactive'
        WHEN m.db_matches_id IS NOT NULL AND m.fnc_status='075' THEN 'confirmed'
        WHEN m.db_matches_id IS NOT NULL AND (m.fnc_host_status='045' OR m.fnc_guest_status='045') THEN 'rejected'
        WHEN m.db_matches_id IS NOT NULL AND (m.fnc_host_status='075' OR m.fnc_guest_status='075') THEN 'being_confirmed'
        WHEN m.db_matches_id IS NOT NULL AND m.fnc_host_status NOT IN ('045', '075') AND m.fnc_guest_status NOT IN ('045', '075') THEN 'found_a_match'
        ELSE 'looking_for_match'
    END AS type

    ,m.db_matches_id AS match_id
    ,CASE
        WHEN m.fnc_status='035' THEN 'timeout'
        WHEN m.fnc_status='045' THEN 'rejected'
        WHEN m.fnc_status='065' THEN 'awaiting_response'
        WHEN m.fnc_status='075' THEN 'accepted'
        ELSE 'default'
    END AS match_status

    ,g.db_guests_id AS guest_id
    ,CASE WHEN m.fnc_status='075' THEN ag.name ELSE '' END AS guest_name
    ,g.city AS guest_city
    ,g.country AS guest_country
    ,CASE WHEN m.fnc_status='075' THEN ag.phone_num ELSE '' END AS guest_phone_num
    ,CASE WHEN m.fnc_status='075' THEN ag.email ELSE '' END AS guest_email
    ,CASE
        WHEN g.fnc_status='045' THEN 'rejected'
        WHEN g.fnc_status='065' THEN 'accepted'
        WHEN g.fnc_status='075' THEN 'being_processed'
        WHEN g.fnc_status='085' THEN 'matched'
        WHEN g.fnc_status='095' THEN 'match_accepted'
        ELSE 'default'
    END AS guest_status
    ,g.acceptable_shelter_types AS guest_acceptable_shelter_types
    ,g.beds AS guest_beds
    ,g.group_relation AS guest_group_relation
    ,g.is_pregnant AS guest_is_pregnant
    ,g.is_with_disability AS guest_is_with_disability
    ,g.is_with_animal AS guest_is_with_animal
    ,g.is_with_elderly AS guest_is_with_elderly
    ,g.is_ukrainian_nationality AS guest_is_ukrainian_nationality
    ,g.duration_category AS guest_duration_category
FROM hosts h
JOIN accounts a ON a.db_accounts_id = h.fnc_accounts_id
LEFT JOIN matches m ON m.fnc_hosts_id = h.db_hosts_id AND m.fnc_status NOT IN ('035', '045')
LEFT JOIN guests g ON g.db_guests_id = m.fnc_guests_id
LEFT JOIN accounts ag ON ag.db_accounts_id = g.fnc_accounts_id
WHERE h.fnc_status != '035';
DROP VIEW IF EXISTS requests;

CREATE OR REPLACE VIEW requests AS
SELECT
    a.uid AS account_uid
    ,a.name AS guest_name

    ,g.db_guests_id AS guest_id
    ,CASE
        WHEN g.fnc_status='035' THEN 'deleted'
        WHEN g.fnc_status='045' THEN 'rejected'
        WHEN g.fnc_status='065' THEN 'accepted'
        WHEN g.fnc_status='075' THEN 'being_processed'
        WHEN g.fnc_status='085' THEN 'matched'
        WHEN g.fnc_status='095' THEN 'match_accepted'
        ELSE 'default'
    END AS guest_status
    ,g.city
    ,g.country
    ,a.phone_num AS phone_num
    ,a.email AS email
    ,g.beds
    ,g.acceptable_shelter_types
    ,g.group_relation
    ,g.is_pregnant
    ,g.is_with_disability
    ,g.is_with_animal
    ,g.is_with_elderly
    ,g.is_ukrainian_nationality
    ,g.duration_category

    ,CASE
        WHEN m.db_matches_id IS NULL THEN 'looking_for_match'
        WHEN m.db_matches_id IS NOT NULL AND m.fnc_status='035' THEN 'inactive'
        WHEN m.db_matches_id IS NOT NULL AND m.fnc_status='075' THEN 'confirmed'
        WHEN m.db_matches_id IS NOT NULL AND (m.fnc_host_status='045' OR m.fnc_guest_status='045') THEN 'rejected'
        WHEN m.db_matches_id IS NOT NULL AND (m.fnc_host_status='075' OR m.fnc_guest_status='075') THEN 'being_confirmed'
        WHEN m.db_matches_id IS NOT NULL AND m.fnc_host_status NOT IN ('045', '075') AND m.fnc_guest_status NOT IN ('045', '075') THEN 'found_a_match'
        ELSE 'looking_for_match'
    END AS type
    
    ,m.db_matches_id AS match_id
    ,CASE
        WHEN m.fnc_status='035' THEN 'timeout'
        WHEN m.fnc_status='045' THEN 'rejected'
        WHEN m.fnc_status='065' THEN 'awaiting_response'
        WHEN m.fnc_status='075' THEN 'accepted'
        ELSE 'default'
    END AS match_status

    ,h.db_hosts_id AS host_id
    ,CASE WHEN m.fnc_status='075' THEN ah.name ELSE '' END AS host_name
    ,h.city AS host_city
    ,h.country AS host_country
    ,CASE WHEN m.fnc_status='075' THEN ah.phone_num ELSE '' END AS host_phone_num
    ,CASE WHEN m.fnc_status='075' THEN ah.email ELSE '' END AS host_email
    ,CASE
        WHEN h.fnc_status='045' THEN 'rejected'
        WHEN h.fnc_status='065' THEN 'accepted'
        WHEN h.fnc_status='075' THEN 'being_processed'
        WHEN h.fnc_status='085' THEN 'matched'
        WHEN h.fnc_status='095' THEN 'match_accepted'
        ELSE 'default'
    END AS host_status
    ,h.shelter_type AS host_shelter_type
    ,h.beds AS host_beds
    ,h.acceptable_group_relations AS host_acceptable_group_relations
    ,h.ok_for_pregnant AS host_ok_for_pregnant
    ,h.ok_for_disabilities AS host_ok_for_disabilities
    ,h.ok_for_animals AS host_ok_for_animals
    ,h.ok_for_elderly AS host_ok_for_elderly
    ,h.ok_for_any_nationality AS host_ok_for_any_nationality
    ,h.duration_category AS host_duration_category
    ,h.transport_included AS host_transport_included
FROM guests g
JOIN accounts a ON a.db_accounts_id = g.fnc_accounts_id
LEFT JOIN matches m ON m.fnc_guests_id = g.db_guests_id AND m.fnc_status NOT IN ('035', '045')
LEFT JOIN hosts h ON h.db_hosts_id = m.fnc_hosts_id
LEFT JOIN accounts ah ON ah.db_accounts_id = h.fnc_accounts_id
WHERE g.fnc_status != '035';
DROP VIEW IF EXISTS accounts_info;

CREATE OR REPLACE VIEW accounts_info AS
SELECT
    db_accounts_id
    ,fnc_status
    ,uid
    ,name
    ,phone_num
    ,email
    ,CASE
        WHEN fnc_email_status='045' THEN 'rejected'
        WHEN fnc_email_status='065' THEN 'accepted'
        ELSE 'default'
    END AS email_status
    ,CASE
        WHEN fnc_msisdn_status='045' THEN 'rejected'
        WHEN fnc_msisdn_status='065' THEN 'accepted'
        WHEN fnc_msisdn_status='075' THEN 'suspended'
        ELSE 'default'
    END AS phone_status
    ,preferred_lang
FROM accounts;
DROP MATERIALIZED VIEW IF EXISTS beds_statistics;

CREATE MATERIALIZED VIEW IF NOT EXISTS beds_statistics AS
(
    WITH matched_beds AS (
        SELECT sum(coalesce(guests.beds, 0)) AS m_beds
        FROM guests
        INNER JOIN matches ON guests.db_guests_id=matches.fnc_guests_id
        WHERE matches.fnc_status = '075'
    ),
    hosts_beds AS (
        SELECT sum(coalesce(hosts.beds, 0)) AS h_beds
        FROM hosts
        WHERE hosts.fnc_status = '065'
    ),
    guests_beds AS (
        SELECT sum(coalesce(guests.beds, 0)) AS g_beds
        FROM guests
        WHERE guests.fnc_status = '065'
    )
    SELECT m_beds, h_beds, g_beds FROM matched_beds, hosts_beds, guests_beds
)
WITH DATA;
