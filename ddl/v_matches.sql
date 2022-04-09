DROP VIEW IF EXISTS v_matches;

CREATE OR REPLACE VIEW v_matches AS
SELECT
    to_timestamp(cast(db_ts_matched as bigint)/1000)::timestamp AS v_db_ts_matched
    ,CASE
		WHEN fnc_status='035' THEN '035:MATCH_TIMEOUT'
		WHEN fnc_status='045' THEN '045:MATCH_REJECTED'
		WHEN fnc_status='055' THEN '055:DEFAULT'
		WHEN fnc_status='065' THEN '065:FNC_AWAITING_RESPONSE'
		WHEN fnc_status='075' THEN '075:MATCH_ACCEPTED'
	END AS v_fnc_status
    ,CASE
		WHEN fnc_host_status='035' THEN '035:MATCH_TIMEOUT'
		WHEN fnc_host_status='045' THEN '045:MATCH_REJECTED'
		WHEN fnc_host_status='055' THEN '055:DEFAULT'
		WHEN fnc_host_status='065' THEN '065:FNC_AWAITING_RESPONSE'
		WHEN fnc_host_status='075' THEN '075:MATCH_ACCEPTED'
	END AS v_fnc_host_status
    ,CASE
		WHEN fnc_guest_status='035' THEN '035:MATCH_TIMEOUT'
		WHEN fnc_guest_status='045' THEN '045:MATCH_REJECTED'
		WHEN fnc_guest_status='055' THEN '055:DEFAULT'
		WHEN fnc_guest_status='065' THEN '065:FNC_AWAITING_RESPONSE'
		WHEN fnc_guest_status='075' THEN '075:MATCH_ACCEPTED'
	END AS v_fnc_guest_status
    ,*
FROM matches;
