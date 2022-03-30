DROP MATERIALIZED VIEW public.beds_statistics;

CREATE MATERIALIZED VIEW IF NOT EXISTS public.beds_statistics AS
(
    WITH matched_beds AS (
        SELECT sum(coalesce(guests.beds, 0)) AS m_beds FROM guests INNER JOIN matches ON guests.db_guests_id=matches.fnc_guests_id WHERE matches.fnc_status = '075'
    ),
    hosts_beds AS (
        SELECT sum(coalesce(hosts.beds, 0)) AS h_beds FROM hosts WHERE hosts.fnc_status = '065'
    ),
    guests_beds AS (
        SELECT sum(coalesce(guests.beds, 0)) AS g_beds FROM guests WHERE guests.fnc_status = '065'
    )
    SELECT m_beds, h_beds, g_beds FROM matched_beds, hosts_beds, guests_beds
)
WITH DATA;
