DROP MATERIALIZED VIEW IF EXISTS countries_beds_breakdown;

CREATE MATERIALIZED VIEW IF NOT EXISTS countries_beds_breakdown AS
(
	SELECT country, closest_city, sum(coalesce(beds, 0)) as beds FROM hosts WHERE fnc_status = '065' GROUP BY country, closest_city
)
WITH DATA;
