-- Table: public.hosts

-- DROP TABLE public.hosts;

CREATE TABLE IF NOT EXISTS public.hosts
(
    db_hosts_id character varying COLLATE pg_catalog."default",
    fnc_ts_registered character varying(13) COLLATE pg_catalog."default",
    fnc_status character varying COLLATE pg_catalog."default",
    fnc_score integer,
    name character varying COLLATE pg_catalog."default",
    country character varying COLLATE pg_catalog."default",
    phone_num character varying COLLATE pg_catalog."default",
    email character varying COLLATE pg_catalog."default",
    city character varying COLLATE pg_catalog."default",
    children_allowed character varying COLLATE pg_catalog."default",
    pet_allowed character varying COLLATE pg_catalog."default",
    handicapped_allowed character varying COLLATE pg_catalog."default",
    num_people integer,
    period integer,
    pietro integer,
    listing_country character varying COLLATE pg_catalog."default",
    shelter_type character varying COLLATE pg_catalog."default",
    beds integer,
    acceptable_group_relations character varying COLLATE pg_catalog."default",
    ok_for_pregnant character varying COLLATE pg_catalog."default",
    ok_for_disabilities character varying COLLATE pg_catalog."default",
    ok_for_animals character varying COLLATE pg_catalog."default",
    ok_for_elderly character varying COLLATE pg_catalog."default",
    ok_for_any_nationality character varying COLLATE pg_catalog."default",
    duration_category character varying COLLATE pg_catalog."default",
    transport_included character varying COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE public.hosts
    OWNER to postgres;
	
	

-- Table: public.guests

-- DROP TABLE public.guests;

CREATE TABLE IF NOT EXISTS public.guests
(
    db_guests_id character varying COLLATE pg_catalog."default",
    fnc_ts_registered character varying(13) COLLATE pg_catalog."default",
    fnc_status character varying COLLATE pg_catalog."default",
    fnc_score integer,
    name character varying COLLATE pg_catalog."default",
    country character varying COLLATE pg_catalog."default",
    phone_num character varying COLLATE pg_catalog."default",
    email character varying COLLATE pg_catalog."default",
    city character varying COLLATE pg_catalog."default",
    is_children character varying COLLATE pg_catalog."default",
    is_pet character varying COLLATE pg_catalog."default",
    is_handicapped character varying COLLATE pg_catalog."default",
    num_people integer,
    period integer,
    listing_country character varying COLLATE pg_catalog."default",
    acceptable_shelter_types character varying COLLATE pg_catalog."default",
    beds integer,
    group_relation character varying COLLATE pg_catalog."default",
    is_pregnant character varying COLLATE pg_catalog."default",
    is_with_disability character varying COLLATE pg_catalog."default",
    is_with_animal character varying COLLATE pg_catalog."default",
    is_with_elderly character varying COLLATE pg_catalog."default",
    is_ukrainian_nationality character varying COLLATE pg_catalog."default",
    duration_category character varying COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE public.guests
    OWNER to postgres;

	
-- Table: public.matches

-- DROP TABLE public.matches;

CREATE TABLE IF NOT EXISTS public.matches
(
    db_matches_id character varying COLLATE pg_catalog."default",
    fnc_ts_matched character varying(13) COLLATE pg_catalog."default",
    fnc_status character varying COLLATE pg_catalog."default",
    fnc_hosts_id character varying COLLATE pg_catalog."default",
    fnc_guests_id character varying COLLATE pg_catalog."default",
    fnc_host_status character varying COLLATE pg_catalog."default",
    fnc_guest_status character varying COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE public.matches
    OWNER to postgres;


-- Materialized view: public.beds_statistics

-- DROP MATERIALIZED VIEW public.beds_statistics;

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

TABLESPACE pg_default;

ALTER TABLE public.beds_statistics
    OWNER to postgres;
