"""Provision registry for Companies Act, 1994.
Entries come from the project blueprint and are UNVERIFIED until a lawyer attaches
authentic text, source_ref, source_sha256, verified_by and verified_on.
"""
from app.legal.corpus.models import Provision

PROVISIONS = [
    Provision(id="companies_act_1994:s43", statute_id="companies_act_1994", section="43", blueprint_topic="rectification of register (blueprint)"),
    Provision(id="companies_act_1994:s59", statute_id="companies_act_1994", section="59", blueprint_topic="capital reduction (blueprint)"),
    Provision(id="companies_act_1994:s60", statute_id="companies_act_1994", section="60", blueprint_topic="capital reduction (blueprint)"),
    Provision(id="companies_act_1994:s81", statute_id="companies_act_1994", section="81", blueprint_topic="AGM matters (blueprint)"),
    Provision(id="companies_act_1994:s85", statute_id="companies_act_1994", section="85", blueprint_topic="AGM matters (blueprint)"),
    Provision(id="companies_act_1994:s195", statute_id="companies_act_1994", section="195", blueprint_topic="qualification/threshold for s.233 application (blueprint)"),
    Provision(id="companies_act_1994:s233", statute_id="companies_act_1994", section="233", blueprint_topic="oppression / mismanagement remedy (blueprint)"),
    Provision(id="companies_act_1994:s228", statute_id="companies_act_1994", section="228", blueprint_topic="reconstruction / amalgamation (blueprint)"),
    Provision(id="companies_act_1994:s229", statute_id="companies_act_1994", section="229", blueprint_topic="reconstruction / amalgamation (blueprint)"),
]
