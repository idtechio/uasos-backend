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
