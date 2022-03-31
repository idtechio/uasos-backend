DROP VIEW IF EXISTS offers;

CREATE OR REPLACE VIEW offers AS
SELECT
    a.uid AS account_uid
    ,a.name AS host_name

    ,h.db_hosts_id AS host_id
    ,CASE
        WHEN h.fnc_status='045' THEN 'rejected'
        WHEN h.fnc_status='065' THEN 'accepted'
        WHEN h.fnc_status='075' THEN 'being_processed'
        WHEN h.fnc_status='085' THEN 'matched'
        WHEN h.fnc_status='095' THEN 'match_accepted'
        ELSE 'default'
    END AS host_status
    ,h.city
    ,h.country
    ,coalesce(h.phone_num, a.phone_num) AS phone_num
    ,coalesce(h.email, a.email) AS email
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

    ,m.db_matches_id AS match_id
    ,CASE
        WHEN m.fnc_status='035' THEN 'timeout'
        WHEN m.fnc_status='045' THEN 'rejected'
        WHEN m.fnc_status='065' THEN 'awaiting_response'
        WHEN m.fnc_status='075' THEN 'accepted'
        ELSE 'default'
    END AS match_status

    ,g.db_guests_id AS guest_id
    ,ag.name AS guest_name
    ,g.city AS guest_city
    ,g.country AS guest_country
    ,coalesce(g.phone_num, ag.phone_num) AS guest_phone_num
    ,coalesce(g.email, ag.email) AS guest_email
    ,CASE
        WHEN g.fnc_status='045' THEN 'rejected'
        WHEN g.fnc_status='065' THEN 'accepted'
        WHEN g.fnc_status='075' THEN 'being_processed'
        WHEN g.fnc_status='085' THEN 'matched'
        WHEN g.fnc_status='095' THEN 'match_accepted'
        ELSE 'default'
    END AS guest_status
FROM hosts h
JOIN accounts a ON a.db_accounts_id = h.fnc_accounts_id
LEFT JOIN matches m ON m.fnc_hosts_id = h.db_hosts_id
LEFT JOIN guests g ON g.db_guests_id = m.fnc_guests_id
LEFT JOIN accounts ag ON ag.db_accounts_id = g.fnc_accounts_id;
