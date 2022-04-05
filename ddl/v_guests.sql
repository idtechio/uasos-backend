CREATE OR REPLACE VIEW v_guests AS
SELECT
    to_timestamp(cast(db_ts_registered as bigint)/1000)::timestamp AS v_db_ts_registered
    ,CASE
		WHEN fnc_status='035' THEN '035:MOD_DELETED'
		WHEN fnc_status='045' THEN '045:DEFAULT'
		WHEN fnc_status='065' THEN '065:MOD_ACCEPTED'
		WHEN fnc_status='075' THEN '075:FNC_BEING_PROCESSED'
		WHEN fnc_status='085' THEN '085:FNC_MATCHED'
		WHEN fnc_status='095' THEN '095:MATCH_ACCEPTED'
	END AS v_fnc_status
    ,*
FROM guests;
