DROP VIEW IF EXISTS accounts_info;

CREATE VIEW IF NOT EXISTS accounts_info AS
SELECT
    uid
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
