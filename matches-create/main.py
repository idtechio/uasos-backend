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
from sqlalchemy.dialects.postgresql import *

from google.cloud import secretmanager
from dotenv import load_dotenv

DEBUG = True # FIXME :)
current_iteration = datetime.datetime.now()

def query_configuration_context(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    secret_name = f'projects/{os.environ["PROJECT_ID"]}/secrets/{secret_id}/versions/latest'
    response = client.access_secret_version(request={"name": secret_name})
    secret_value = response.payload.data.decode("UTF-8")
    configuration_context = json.loads(secret_value)
    return configuration_context


# Load local .env if not on GCP
running_locally = bool(os.getenv("LOCAL_DEVELOPMENT"))
if not running_locally:
    configuration_context = query_configuration_context(os.environ["SECRET_CONFIGURATION_CONTEXT"])
else:
    print(f"Running locally")
    load_dotenv()


#region Database
def create_db_engine():
    db_config = {
        "drivername": "postgresql+pg8000",
    }
    if not running_locally:
        db_connection_name = os.environ["DB_CONNECTION_NAME"]
        db_config |= {
            "query": dict({"unix_sock": f"/cloudsql/{db_connection_name}/.s.PGSQL.5432"}),
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
        sqlalchemy.engine.url.URL.create(
            **db_config
        ),
    )
    pool.dialect.description_encoding = None
    return pool


db = create_db_engine()
#endregion


#region Enum definitions
class MatchesStatus(Enum):
    DEFAULT 			  = '055'
    FNC_AWAITING_RESPONSE = '065'
    MATCH_ACCEPTED 		  = '075'
    MATCH_REJECTED		  = '045'


class HostsGuestsStatus(Enum):
    MOD_REJECTED 		= '045'
    DEFAULT 			= '055'
    MOD_ACCEPTED  		= '065'
    FNC_BEING_PROCESSED = '075'
    FNC_MATCHED 		= '085'
    MATCH_ACCEPTED 		= '095'
#endregion


#region DataScience structures
@dataclasses.dataclass
class HostListing:
    """Illustrative description of a Polish host and their housing offer."""

    rid: str
    name: str
    last_modification_date: datetime.datetime
    listing_country: str
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
    name: str
    listing_country: str
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
#endregion


#region DataScience functions
def evaluate_pair(host, guest):
    """Check whether a `host` could potentially satisfy a `guest`'s needs.

    Return 0.0 if match is impossible.

    Return a value 0.0 < score <= 1.0 if match is possible.
    The higher the score, the better fit there is between the host and the guest.
    """


    if host.listing_country != guest.listing_country:
        return 0.0

    if host.shelter_type not in guest.acceptable_shelter_types:
        return 0.0

    if host.beds < guest.beds:
        return 0.0

    if guest.group_relation not in host.acceptable_group_relations:
        return 0.0

    if not host.ok_for_pregnant and guest.is_pregnant:
        return 0.0

    if not host.ok_for_disabilities and guest.is_with_disability:
        return 0.0

    if not host.ok_for_animals and guest.is_with_animal:
        return 0.0

    if not host.ok_for_elderly and guest.is_with_elderly:
        return 0.0

    if not host.ok_for_any_nationality and not guest.is_ukrainian_nationality:
        return 0.0

    if host.duration_category < guest.duration_category:
        return 0.0

    empty_beds = host.beds - guest.beds

    listing_age_in_days = (datetime.datetime.now() - host.last_modification_date).days

    score = 0.0

    score += 0.4 * (1.0 - min(empty_beds, 4) / 4.0)

    score += 0.2 * int(host.listing_city == guest.listing_city)

    score += 0.2 * (listing_age_in_days / 7.0)

    score += 0.1 * int(host.transport_included)

    score += 0.1 * int(host.duration_category == guest.duration_category)

    print(f"probing match (guest={guest.rid}, host={host.rid}) with scoring {score}")

    return score


def find_matches(hosts, guests):
    """Match hosts and guests, maximizing the sum of matching scores.  Return matched pairs."""

    # Set up the cost matrix.  As the Hungarian algorithm minimizes cost,
    # use negative score as cost in order to maximize score
    cost_matrix = np.array([[-evaluate_pair(h, g) for g in guests] for h in hosts])

    # Run the Hungarian algorithm
    host_indices, guest_indices = scipy.optimize.linear_sum_assignment(cost_matrix)

    # Collect results, throwing away assignments with zero score, which signify lack of match.
    matches = [(hosts[hi], guests[gi]) for hi, gi in zip(host_indices, guest_indices) if cost_matrix[hi, gi] < 0.0]

    return matches
#endregion


#region Database data models
def create_matches_table_mapping():
    table_name = os.environ["MATCHES_TABLE_NAME"]
    # table_name = 'matches'
    meta = MetaData(db)
    tbl = Table(table_name, meta,
                Column('db_matches_id', VARCHAR),
                Column('fnc_ts_matched', VARCHAR),
                Column('fnc_status', VARCHAR),
                Column('fnc_hosts_id', VARCHAR),
                Column('fnc_guests_id', VARCHAR),
                Column('fnc_host_status', VARCHAR),
                Column('fnc_guest_status', VARCHAR)
                )

    return tbl


def create_guests_table_mapping():
    table_name = os.environ["GUESTS_TABLE_NAME"]
    # table_name = 'guests'
    meta = MetaData(db)
    tbl = Table(table_name, meta,
                Column('db_guests_id', VARCHAR),
                Column('name', VARCHAR),
                Column('city', VARCHAR),
                Column('fnc_status', VARCHAR),
                Column('listing_country', VARCHAR),
                Column('acceptable_shelter_types', VARCHAR),
                Column('beds', VARCHAR),
                Column('group_relation', VARCHAR),
                Column('is_pregnant', VARCHAR),
                Column('is_with_disability', VARCHAR),
                Column('is_with_animal', VARCHAR),
                Column('is_with_elderly', VARCHAR),
                Column('is_ukrainian_nationality', VARCHAR),
                Column('duration_category', VARCHAR)
                )

    return tbl


def create_hosts_table_mapping():
    table_name = os.environ["HOSTS_TABLE_NAME"]
    # table_name = 'hosts'
    meta = MetaData(db)
    tbl = Table(table_name, meta,
                Column('db_hosts_id', VARCHAR),
                Column('name', VARCHAR),
                Column('fnc_status', VARCHAR),
                Column('fnc_ts_registered', VARCHAR),
                Column('city', VARCHAR),
                Column('listing_country', VARCHAR),
                Column('shelter_type', VARCHAR),
                Column('beds', VARCHAR),
                Column('acceptable_group_relations', VARCHAR),
                Column('ok_for_pregnant', VARCHAR),
                Column('ok_for_disabilities', VARCHAR),
                Column('ok_for_animals', VARCHAR),
                Column('ok_for_elderly', VARCHAR),
                Column('ok_for_any_nationality', VARCHAR),
                Column('duration_category', VARCHAR)
                )

    return tbl
#endregion

#region Utility functions
def query_list(input_text):
    return input_text.split(',')


def epoch_with_milliseconds_to_datetime(input):
    return datetime.datetime.fromtimestamp(int(input[:-3]))


def query_epoch_with_milliseconds():
    return int(time.time() * 1000)
#endregion


#region Database mutation functions
def change_host_status(db_connection, db_hosts_id, target_status):
    tbl = create_hosts_table_mapping()

    upd = (
        tbl.update()
            .where(tbl.c.db_hosts_id==db_hosts_id)
            .values(fnc_status=target_status)
    )

    # with pool.connect() as conn:
    db_connection.execute(upd)


def change_guest_status(db_connection, db_guests_id, target_status):
    tbl = create_guests_table_mapping()

    upd = (
        tbl.update()
            .where(tbl.c.db_guests_id==db_guests_id)
            .values(fnc_status=target_status)
    )

    # with pool.connect() as conn:
    db_connection.execute(upd)
#endregion


#region PubSub Topic consumer endpoint
def fnc_target(event, context):
    if not running_locally:
        pubsub_msg = json.loads(base64.b64decode(event['data']).decode('utf-8'))
    else:
        pubsub_msg = json.loads(event['data'])

    create_matching(pubsub_msg)
#endregion


#region Main function
def create_matching(pubsub_msg):
    HOSTS_MATCHING_BATCH_SIZE=configuration_context('HOSTS_MATCHING_BATCH_SIZE')
    GUESTS_MATCHING_BATCH_SIZE=configuration_context('GUESTS_MATCHING_BATCH_SIZE')
    MATCHES_INITIAL_STATUS=os.environ["MATCHES_INITIAL_STATUS"]

    tbl_matches = create_matches_table_mapping()
    tbl_guests = create_guests_table_mapping()
    tbl_hosts = create_hosts_table_mapping()

#region Preparing hosts dataset
    hosts = []

    sel_hosts = (
        tbl_hosts.select().limit(HOSTS_MATCHING_BATCH_SIZE)
            .where(tbl_hosts.c.fnc_status == HostsGuestsStatus.MOD_ACCEPTED)
    )

    with db.connect() as conn:
        with conn.begin():
            result = conn.execute(sel_hosts)

            for row in result:
                print(epoch_with_milliseconds_to_datetime(row['fnc_ts_registered']))

                hosts.append(HostListing(
                    rid = row['db_hosts_id'],
                    name = row['name'],
                    last_modification_date = epoch_with_milliseconds_to_datetime(row['fnc_ts_registered']),
                    listing_country = row['listing_country'],
                    listing_city = row['city'],
                    shelter_type = row['shelter_type'],
                    beds = int(row['beds']),
                    acceptable_group_relations = query_list(row['acceptable_group_relations']),
                    ok_for_any_nationality = eval(row['ok_for_any_nationality']),
                    ok_for_elderly = eval(row['ok_for_elderly']),
                    ok_for_pregnant = eval(row['ok_for_pregnant']),
                    ok_for_disabilities = eval(row['ok_for_disabilities']),
                    ok_for_animals = eval(row['ok_for_animals']),
                    duration_category = int(row['duration_category']),
                    transport_included = True # FIXME: placeholder
                ))
                print(f"added to HOSTS list {row['db_hosts_id']}")

            if DEBUG:
                print(hosts)

            for host in hosts:
                change_host_status(conn, host.rid, HostsGuestsStatus.FNC_BEING_PROCESSED)
#endregion

#region Preparing guests dataset
    guests = []

    sel_guests = (
        tbl_guests.select().limit(GUESTS_MATCHING_BATCH_SIZE)
            .where(tbl_guests.c.fnc_status == HostsGuestsStatus.MOD_ACCEPTED)
    )

    with db.connect() as conn:
        with conn.begin():
            result = conn.execute(sel_guests)

            for row in result:
                guests.append(GuestListing(
                    rid = row['db_guests_id'],
                    name = row['name'],
                    listing_country = row['listing_country'],
                    listing_city = row['city'],
                    beds = int(row['beds']),
                    is_pregnant = eval(row['is_pregnant']),
                    is_with_disability = eval(row['is_with_disability']),
                    is_with_animal = eval(row['is_with_animal']),
                    is_with_elderly = eval(row['is_with_elderly']),
                    group_relation = row['group_relation'],
                    acceptable_shelter_types = query_list(row['acceptable_shelter_types']),
                    is_ukrainian_nationality = bool(row['is_ukrainian_nationality']),
                    duration_category = int(row['duration_category'])
                ))
                print(f"added to GUESTS list {row['db_guests_id']}")

            if DEBUG:
                print(guests)

            for guest in guests:
                change_guest_status(conn, guest.rid, HostsGuestsStatus.FNC_BEING_PROCESSED)
#endregion

#region Looking for matches
    matches = find_matches(hosts, guests)
    print(f"found best matches in iteration {current_iteration}: {len(matches)}")

    for host, guest in matches:
        print(f"match (guest={guest.rid}, host={host.rid})")

        ins_match = (
            tbl_matches.insert().values(
                fnc_ts_matched=f'{query_epoch_with_milliseconds()}',
                fnc_status=MATCHES_INITIAL_STATUS,
                fnc_hosts_id=host.rid,
                fnc_guests_id=guest.rid,
                fnc_host_status=MATCHES_INITIAL_STATUS,
                fnc_guest_status=MATCHES_INITIAL_STATUS
            )
        )

        with db.connect() as conn:
            with conn.begin():
                conn.execute(ins_match)

                for element in hosts:
                    if element.rid != host.rid:
                        change_host_status(conn, element.rid, HostsGuestsStatus.FNC_MATCHED)
                    else:
                        change_host_status(conn, element.rid, HostsGuestsStatus.MOD_ACCEPTED)


                for element in guests:
                    if element.rid != guest.rid:
                        change_guest_status(conn, element.rid, HostsGuestsStatus.FNC_MATCHED)
                    else:
                        change_guest_status(conn, element.rid, HostsGuestsStatus.MOD_ACCEPTED)
#endregion

#endregion
