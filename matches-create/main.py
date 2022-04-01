import dataclasses
import datetime
import numpy as np
import scipy.optimize

import os
import sqlalchemy
import base64
import json
import time
from enum import Enum
from sqlalchemy import create_engine
from sqlalchemy import Table
from sqlalchemy import MetaData
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import VARCHAR

from google.cloud import secretmanager
from dotenv import load_dotenv

DEBUG = False  # FIXME :)
current_iteration = datetime.datetime.now()

# IMPORTANT Order of values must be ascending!!!!
DURATION_CATEGORIES = ["less_than_1_week", "1_week", "2_3_weeks", "month", "longer"]
MATCH_TIMEOUT_HOURS = None


def query_configuration_context(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    secret_name = (
        f'projects/{os.environ["PROJECT_ID"]}/secrets/{secret_id}/versions/latest'
    )
    response = client.access_secret_version(request={"name": secret_name})
    secret_value = response.payload.data.decode("UTF-8")
    configuration_context = json.loads(secret_value)
    return configuration_context


# Load local .env if not on GCP
running_locally = bool(os.getenv("LOCAL_DEVELOPMENT"))
if not running_locally:
    configuration_context = query_configuration_context(
        os.environ["SECRET_CONFIGURATION_CONTEXT"]
    )
else:
    print("Running locally")
    load_dotenv()


# region Database
def create_db_engine():
    db_config = {
        "drivername": "postgresql+pg8000",
    }
    if not running_locally:
        db_connection_name = os.environ["DB_CONNECTION_NAME"]
        db_config |= {
            "query": dict(
                {"unix_sock": f"/cloudsql/{db_connection_name}/.s.PGSQL.5432"}
            ),
            "database": configuration_context["DB_NAME"],
            "username": configuration_context["DB_USER"],
            "password": configuration_context["DB_PASS"],
        }
    else:
        db_config |= {
            "host": os.environ["DB_HOST"],
            "port": os.environ["DB_PORT"],
            "database": os.environ["DB_NAME"],
            "username": os.environ["DB_USER"],
            "password": os.environ["DB_PASS"],
        }
    pool = create_engine(
        sqlalchemy.engine.url.URL.create(**db_config),
    )
    pool.dialect.description_encoding = None
    return pool


db = create_db_engine()
# endregion


# region Enum definitions
class MatchesStatus(Enum):
    DEFAULT = "055"
    FNC_AWAITING_RESPONSE = "065"
    MATCH_ACCEPTED = "075"
    MATCH_REJECTED = "045"
    MATCH_TIMEOUT = "035"


class HostsGuestsStatus(Enum):
    MOD_REJECTED = "045"
    DEFAULT = "055"
    MOD_ACCEPTED = "065"
    FNC_BEING_PROCESSED = "075"
    FNC_MATCHED = "085"
    MATCH_ACCEPTED = "095"


# endregion


# region DataScience structures
@dataclasses.dataclass
class HostListing:
    """Illustrative description of a Polish host and their housing offer."""

    rid: str
    registration_date: datetime.datetime
    country: str
    listing_city: str
    shelter_type: str
    beds: int
    acceptable_group_relations: list
    ok_for_any_nationality: bool
    ok_for_elderly: bool
    ok_for_pregnant: bool
    ok_for_disabilities: bool
    ok_for_animals: bool
    duration_category: int
    transport_included: bool


@dataclasses.dataclass
class GuestListing:
    """Illustrative description of a Ukranian refugee and their housing need."""

    rid: str
    registration_date: datetime.datetime
    country: str
    listing_city: str
    beds: int
    is_pregnant: bool
    is_with_disability: bool
    is_with_animal: bool
    is_with_elderly: bool
    group_relation: str
    acceptable_shelter_types: list
    is_ukrainian_nationality: bool
    duration_category: int


# endregion


# region DataScience functions
def evaluate_pair(host: HostListing, guest: GuestListing, recent_matches, rid_pairs):
    """Check whether a `host` could potentially satisfy a `guest`'s needs.

    Return 0.0 if match is impossible.

    Return a value 0.0 < score <= 1.0 if match is possible.
    The higher the score, the better fit there is between the host and the guest.
    """

    # Hard constraints
    if guest.country != host.country:
        return 0.0
    if guest.is_pregnant and not host.ok_for_pregnant:
        return 0.0
    if guest.is_with_disability and not host.ok_for_disabilities:
        return 0.0
    if guest.is_with_animal and not host.ok_for_animals:
        return 0.0
    if guest.is_with_elderly and not host.ok_for_elderly:
        return 0.0
    if not guest.is_ukrainian_nationality and not host.ok_for_any_nationality:
        return 0.0
    if host.duration_category < guest.duration_category:
        return 0.0
    if guest.group_relation not in host.acceptable_group_relations:
        return 0.0
    if host.shelter_type not in guest.acceptable_shelter_types:
        return 0.0
    if host.beds < guest.beds:
        return 0.0
    if (host.rid, guest.rid) in rid_pairs:
        return 0.0
    if host.listing_city != guest.listing_city and guest.listing_city is not None:
        return 0.0

    # Soft constraints

    # Score composition:
    #  79% -> Guarant -> after passing hard constrants people should be ready to match
    #  1% -> Transport included
    #  5% -> Boosters for host activity related to response rate for previous offers
    #  5% -> Boosters for guest activity related to response rate for previous offers
    #  5% -> Boosters for recency of host registration
    #  5% -> Boosters for recency of guest registration

    score = 0.79

    # -> Transport included
    score += 0.01 * int(host.transport_included)

    # -> Boosters for host and guest activity related to response rate for previous offers #FIXME Optimize execution (otherwise function invocations may time out)
    # Calculate activity score
    # host_activity_boost = 0
    # guest_activity_boost = 0

    # for row in recent_matches:
    #     if row["fnc_hosts_id"] == host.rid and (
    #         row["fnc_host_status"] == MatchesStatus.MATCH_ACCEPTED.value
    #         or row["fnc_host_status"] == MatchesStatus.MATCH_REJECTED.value
    #     ):
    #         if row["fnc_status"] == MatchesStatus.MATCH_TIMEOUT.value:
    #             host_activity_boost += 3
    #         if row["fnc_status"] == MatchesStatus.MATCH_REJECTED.value:
    #             host_activity_boost += 1
    #     if row["fnc_guests_id"] == guest.rid and (
    #         row["fnc_guest_status"] == MatchesStatus.MATCH_ACCEPTED.value
    #         or row["fnc_guest_status"] == MatchesStatus.MATCH_REJECTED.value
    #     ):
    #         if row["fnc_status"] == MatchesStatus.MATCH_TIMEOUT.value:
    #             guest_activity_boost += 3
    #         if row["fnc_status"] == MatchesStatus.MATCH_REJECTED.value:
    #             guest_activity_boost += 1

    # score += 0.05 * float(min(6, host_activity_boost) / 6.0)
    # score += 0.05 * float(min(6, guest_activity_boost) / 6.0)

    # -> Boosters for recency of host registration
    host_listing_age = age_in_hours(host.registration_date)
    score += 0.05 * max(
        0.0, 1.0 - float(host_listing_age) / 2.0 / float(MATCH_TIMEOUT_HOURS)
    )

    # -> Boosters for recency of guest registration
    guest_listing_age = age_in_hours(guest.registration_date)
    score += 0.05 * max(
        0.0, 1.0 - float(guest_listing_age) / 2.0 / float(MATCH_TIMEOUT_HOURS)
    )

    return score


def find_matches(hosts, guests, recent_matches, rid_pairs):
    """Match hosts and guests, maximizing the sum of matching scores.  Return matched pairs."""

    # Set up the cost matrix.  As the Hungarian algorithm minimizes cost,
    # use negative score as cost in order to maximize score
    print("Creating cost_matrix")
    cost_matrix = np.array(
        [
            [-evaluate_pair(h, g, recent_matches, rid_pairs) for g in guests]
            for h in hosts
        ]
    )
    print("Finished creating cost_matrix")

    if DEBUG:
        print("Guests:")
        print(guests)
        print("Hosts:")
        print(hosts)
        print(cost_matrix)
    # Run the Hungarian algorithm
    host_indices, guest_indices = scipy.optimize.linear_sum_assignment(cost_matrix)

    # Collect results, throwing away assignments with zero score, which signify lack of match.
    matches = [
        (hosts[hi], guests[gi])
        for hi, gi in zip(host_indices, guest_indices)
        if cost_matrix[hi, gi] < 0.0
    ]

    return matches


# endregion


# region Database data models
def create_matches_table_mapping():
    table_name = os.environ["MATCHES_TABLE_NAME"]
    meta = MetaData(db)
    tbl = Table(
        table_name,
        meta,
        Column("db_matches_id", VARCHAR),
        Column("fnc_ts_matched", VARCHAR),
        Column("fnc_status", VARCHAR),
        Column("fnc_hosts_id", VARCHAR),
        Column("fnc_guests_id", VARCHAR),
        Column("fnc_host_status", VARCHAR),
        Column("fnc_guest_status", VARCHAR),
    )

    return tbl


def create_guests_table_mapping():
    table_name = os.environ["GUESTS_TABLE_NAME"]
    # table_name = 'guests'
    meta = MetaData(db)
    tbl = Table(
        table_name,
        meta,
        Column("db_guests_id", VARCHAR),
        Column("city", VARCHAR),
        Column("fnc_status", VARCHAR),
        Column("db_ts_registered", VARCHAR),
        Column("country", VARCHAR),
        Column("acceptable_shelter_types", VARCHAR),
        Column("beds", VARCHAR),
        Column("group_relation", VARCHAR),
        Column("is_pregnant", VARCHAR),
        Column("is_with_disability", VARCHAR),
        Column("is_with_animal", VARCHAR),
        Column("is_with_elderly", VARCHAR),
        Column("is_ukrainian_nationality", VARCHAR),
        Column("duration_category", VARCHAR),
    )

    return tbl


def create_hosts_table_mapping():
    table_name = os.environ["HOSTS_TABLE_NAME"]
    # table_name = 'hosts'
    meta = MetaData(db)
    tbl = Table(
        table_name,
        meta,
        Column("db_hosts_id", VARCHAR),
        Column("fnc_status", VARCHAR),
        Column("db_ts_registered", VARCHAR),
        Column("city", VARCHAR),
        Column("country", VARCHAR),
        Column("shelter_type", VARCHAR),
        Column("beds", VARCHAR),
        Column("acceptable_group_relations", VARCHAR),
        Column("ok_for_pregnant", VARCHAR),
        Column("ok_for_disabilities", VARCHAR),
        Column("ok_for_animals", VARCHAR),
        Column("ok_for_elderly", VARCHAR),
        Column("ok_for_any_nationality", VARCHAR),
        Column("duration_category", VARCHAR),
    )

    return tbl


# endregion

# region Utility functions
def query_list(input_text):
    if type(input_text) != str:
        return []
    return input_text.strip("{ }").split(",")


def query_string(input_text):
    # FIXME Should strings be kept in DB as {str}, with parenthesis
    return input_text.strip("{ }")


def epoch_with_milliseconds_to_datetime(input):
    return datetime.datetime.fromtimestamp(int(input[:-3]))


def age_in_hours(t: datetime.datetime):
    n = datetime.datetime.now()
    return (n - t).days * 24 + int((n - t).seconds / 3600)


def default_value(value: str, default: str):
    # FIXME: null to poland should be set in service writing to DB
    if value is None:
        return default
    else:
        return value


def query_epoch_with_milliseconds():
    return int(time.time() * 1000)


# endregion


# region Database mutation functions
def change_host_status(db_connection, db_hosts_id, target_status):
    tbl = create_hosts_table_mapping()

    upd = (
        tbl.update()
        .where(tbl.c.db_hosts_id == db_hosts_id)
        .values(fnc_status=target_status)
    )

    # with pool.connect() as conn:
    db_connection.execute(upd)


def change_guest_status(db_connection, db_guests_id, target_status):
    tbl = create_guests_table_mapping()

    upd = (
        tbl.update()
        .where(tbl.c.db_guests_id == db_guests_id)
        .values(fnc_status=target_status)
    )

    # with pool.connect() as conn:
    db_connection.execute(upd)


# endregion


# region PubSub Topic consumer endpoint
def fnc_target(event, context):
    if not running_locally:
        pubsub_msg = json.loads(base64.b64decode(event["data"]).decode("utf-8"))
    else:
        pubsub_msg = json.loads(event["data"])

    create_matching(pubsub_msg)


# endregion


# region Main function
def create_matching(pubsub_msg):
    HOSTS_MATCHING_BATCH_SIZE = configuration_context["HOSTS_MATCHING_BATCH_SIZE"]
    GUESTS_MATCHING_BATCH_SIZE = configuration_context["GUESTS_MATCHING_BATCH_SIZE"]
    global MATCH_TIMEOUT_HOURS
    MATCH_TIMEOUT_HOURS = configuration_context["MATCH_TIMEOUT_HOURS"]

    tbl_matches = create_matches_table_mapping()
    tbl_guests = create_guests_table_mapping()
    tbl_hosts = create_hosts_table_mapping()

    # region Preparing hosts dataset
    print("Preparing hosts dataset")
    hosts = []

    sel_hosts = (
        tbl_hosts.select()
        .limit(HOSTS_MATCHING_BATCH_SIZE)
        .where(tbl_hosts.c.fnc_status == HostsGuestsStatus.MOD_ACCEPTED)
    )

    with db.connect() as conn:
        with conn.begin():
            result = conn.execute(sel_hosts)

            for row in result:

                hosts.append(
                    HostListing(
                        rid=row["db_hosts_id"],
                        registration_date=epoch_with_milliseconds_to_datetime(
                            row["db_ts_registered"]
                        ),
                        country=default_value(row["country"], "poland"),
                        listing_city=row["city"],
                        shelter_type=query_string(row["shelter_type"]),
                        beds=int(row["beds"]),
                        acceptable_group_relations=query_list(
                            row["acceptable_group_relations"]
                        ),
                        ok_for_any_nationality=True
                        if row["ok_for_any_nationality"] == "TRUE"
                        else False,
                        ok_for_elderly=True
                        if row["ok_for_elderly"] == "TRUE"
                        else False,
                        ok_for_pregnant=True
                        if row["ok_for_pregnant"] == "TRUE"
                        else False,
                        ok_for_disabilities=True
                        if row["ok_for_disabilities"] == "TRUE"
                        else False,
                        ok_for_animals=True
                        if row["ok_for_animals"] == "TRUE"
                        else False,
                        duration_category=DURATION_CATEGORIES.index(
                            query_string(row["duration_category"])
                        ),
                        transport_included=False,  # FIXME: placeholder
                    )
                )
                # print(f"added to HOSTS list {row['db_hosts_id']}")

            if DEBUG:
                print(hosts)
            print("Changing fnc_status to '075' in hosts dataset")

            for host in hosts:
                change_host_status(
                    conn, host.rid, HostsGuestsStatus.FNC_BEING_PROCESSED
                )
    # endregion

    # region Preparing guests dataset
    print("Preparing guests dataset")
    guests = []

    sel_guests = (
        tbl_guests.select()
        .limit(GUESTS_MATCHING_BATCH_SIZE)
        .where(tbl_guests.c.fnc_status == HostsGuestsStatus.MOD_ACCEPTED)
    )

    with db.connect() as conn:
        with conn.begin():
            result = conn.execute(sel_guests)

            for row in result:
                guests.append(
                    GuestListing(
                        rid=row["db_guests_id"],
                        registration_date=epoch_with_milliseconds_to_datetime(
                            row["db_ts_registered"]
                        ),
                        country=default_value(row["country"], "poland"),
                        listing_city=row["city"],
                        beds=int(row["beds"]),
                        is_pregnant=True if row["is_pregnant"] == "TRUE" else False,
                        is_with_disability=True
                        if row["is_with_disability"] == "TRUE"
                        else False,
                        is_with_animal=True
                        if row["is_with_animal"] == "TRUE"
                        else False,
                        is_with_elderly=True
                        if row["is_with_elderly"] == "TRUE"
                        else False,
                        group_relation=query_string(row["group_relation"]),
                        acceptable_shelter_types=query_list(
                            row["acceptable_shelter_types"]
                        ),
                        is_ukrainian_nationality=True
                        if row["is_ukrainian_nationality"] == "TRUE"
                        else False,
                        duration_category=DURATION_CATEGORIES.index(
                            query_string(row["duration_category"])
                        ),
                    )
                )
                # print(f"added to GUESTS list {row['db_guests_id']}")

            if DEBUG:
                print(guests)
            print("Changing fnc_status to '075' in guests dataset")

            for guest in guests:
                change_guest_status(
                    conn, guest.rid, HostsGuestsStatus.FNC_BEING_PROCESSED
                )
    # endregion

    # region Getting historical matches
    print("Getting historical matches")

    with db.connect() as conn:
        with conn.begin():

            # Create rid_pairs set
            existing_pairs_stmt = sqlalchemy.text(
                f"SELECT DISTINCT ma.fnc_ts_matched, ma.fnc_hosts_id, ma.fnc_guests_id FROM matches ma JOIN hosts ho ON ma.fnc_hosts_id = ho.db_hosts_id JOIN guests gu ON ma.fnc_guests_id = gu.db_guests_id WHERE ho.fnc_status = '075' OR gu.fnc_status = '075';"
            )
            existing_pairs_result = conn.execute(existing_pairs_stmt)
            rid_pairs = set()
            for row in existing_pairs_result:
                rid_pairs.add((row["fnc_hosts_id"], row["fnc_guests_id"]))
                
            # Create recent_matches list
            sel_matches_stmt = tbl_matches.select()
            sel_matches_result = conn.execute(sel_matches_stmt)
            recent_matches = []
            # day filter equals 3* timeout. If it would be 2*timeout we would almost always cut of the match whose timeout is
            # approxemetely 2 timeouts ago.
            day_filter = str(
                int(
                    (
                        datetime.datetime.now()
                        - datetime.timedelta(hours=3 * int(MATCH_TIMEOUT_HOURS))
                    ).timestamp()
                    * 1000
                )
            )
            for row in sel_matches_result:
                if row["fnc_ts_matched"] > day_filter:
                    recent_matches.append(row)

    # endregion

    # region Looking for matches
    print("Looking for matches")
    matches = []
    if len(hosts) > 0 and len(guests) > 0:
        matches = find_matches(hosts, guests, recent_matches, rid_pairs)
    # print(f"found best matches in iteration {current_iteration}: {len(matches)}")
    print(f"found best matches in iteration {current_iteration}")

    with db.connect() as conn:
        with conn.begin():
            print(f"Inserting matches and updating statuses")
            for host, guest in matches:
                # print(f"match (guest={guest.rid}, host={host.rid})")

                ins_match = tbl_matches.insert().values(
                    fnc_ts_matched=f"{query_epoch_with_milliseconds()}",
                    fnc_status=MatchesStatus.DEFAULT,
                    fnc_hosts_id=host.rid,
                    fnc_guests_id=guest.rid,
                    fnc_host_status=MatchesStatus.DEFAULT,
                    fnc_guest_status=MatchesStatus.DEFAULT,
                )

                conn.execute(ins_match)

            matched_hosts = [host.rid for host, guest in matches]
            matched_guests = [guest.rid for host, guest in matches]

            for element in hosts:
                if element.rid in matched_hosts:
                    change_host_status(conn, element.rid, HostsGuestsStatus.FNC_MATCHED)
                else:
                    change_host_status(
                        conn, element.rid, HostsGuestsStatus.MOD_ACCEPTED
                    )

            for element in guests:
                if element.rid in matched_guests:
                    change_guest_status(
                        conn, element.rid, HostsGuestsStatus.FNC_MATCHED
                    )
                else:
                    change_guest_status(
                        conn, element.rid, HostsGuestsStatus.MOD_ACCEPTED
                    )


# endregion

# endregion
