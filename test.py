from enum import Enum


class MatchesStatus(Enum):
    DEFAULT = "055"
    FNC_AWAITING_RESPONSE = "065"
    MATCH_ACCEPTED = "075"
    MATCH_REJECTED = "045"
    MATCH_TIMEOUT = "035"
 
 
pubsub_msg = {'fnc_status': "065"}

if pubsub_msg['fnc_status'] != MatchesStatus.FNC_AWAITING_RESPONSE.value:
    print('is not')
else:
    print('is')

print('test')