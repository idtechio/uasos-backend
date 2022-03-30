DROP VIEW IF EXISTS offers;

CREATE VIEW IF NOT EXISTS requests AS
SELECT
    a.uid AS account_uid

    ,g.db_guests_id AS guest_id
    ,CASE
        WHEN g.fnc_status='045' THEN 'rejected'
        WHEN g.fnc_status='065' THEN 'accepted'
        WHEN g.fnc_status='075' THEN 'being_processed'
        WHEN g.fnc_status='085' THEN 'matched'
        WHEN g.fnc_status='095' THEN 'match_accepted'
        ELSE 'default'
    END AS guest_status
    ,g.city
    ,g.country
    ,g.phone_num
    ,g.email
    ,g.beds
    ,g.acceptable_shelter_types
    ,g.group_relation
    ,g.duration_category
    ,g.is_pregnant
    ,g.is_with_disability
    ,g.is_with_animal
    ,g.is_with_elderly
    ,g.is_ukrainian_nationality
    ,g.duration_category
    
    ,m.db_matches_id AS match_id
    ,CASE
        WHEN m.fnc_status='035' THEN 'timeout'
        WHEN m.fnc_status='045' THEN 'rejected'
        WHEN m.fnc_status='065' THEN 'awaiting_response'
        WHEN m.fnc_status='075' THEN 'accepted'
        ELSE 'default'
    END AS match_status

    ,h.db_hosts_id AS host_id
    ,h.city AS host_city
    ,h.country AS host_country
    ,h.phone_num AS host_phone_num
    ,h.email AS host_email
    ,CASE
        WHEN h.fnc_status='045' THEN 'rejected'
        WHEN h.fnc_status='065' THEN 'accepted'
        WHEN h.fnc_status='075' THEN 'being_processed'
        WHEN h.fnc_status='085' THEN 'matched'
        WHEN h.fnc_status='095' THEN 'match_accepted'
        ELSE 'default'
    END AS hosts_status
FROM hosts h
JOIN accounts a ON a.db_accounts_id = h.fnc_accounts_id
LEFT JOIN matches m ON m.fnc_hosts_id = h.db_hosts_id
LEFT JOIN guests g ON g.db_guests_id = m.fnc_guests_id;
