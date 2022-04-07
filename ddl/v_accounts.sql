CREATE OR REPLACE VIEW v_accounts AS
SELECT
    to_timestamp(cast(db_ts_registered as bigint)/1000)::timestamp AS v_db_ts_registered
    ,CASE
		WHEN fnc_status='035' THEN '035:MOD_TO_MIGRATE'
		WHEN fnc_status='045' THEN '045:MOD_REJECTED'
		WHEN fnc_status='055' THEN '055:DEFAULT'
		WHEN fnc_status='065' THEN '065:MOD_ACCEPTED'
	END AS v_fnc_status
    ,*
FROM accounts;
