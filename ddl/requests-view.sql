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
    ,coalesce(g.phone_num, a.phone_num) AS phone_num
    ,coalesce(g.email, a.email) AS email
    ,g.beds
    ,g.acceptable_shelter_types
    ,g.group_relation
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
    ,ah.name AS host_name
    ,h.city AS host_city
    ,h.country AS host_country
    ,coalesce(h.phone_num, ah.phone_num) AS host_phone_num
    ,coalesce(h.email, ah.email) AS host_email
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
LEFT JOIN matches m ON m.fnc_guests_id = g.db_guests_id
LEFT JOIN hosts h ON h.db_hosts_id = m.fnc_hosts_id
LEFT JOIN accounts ah ON ah.db_accounts_id = h.fnc_accounts_id
WHERE g.fnc_status != '035';
