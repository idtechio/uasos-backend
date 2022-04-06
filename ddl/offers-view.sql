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
    ,h.host_type
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
