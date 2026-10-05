"""Provision registry for Code of Civil Procedure, 1908.
Entries come from the project blueprint and are UNVERIFIED until a lawyer attaches
authentic text, source_ref, source_sha256, verified_by and verified_on.
"""
from app.legal.corpus.models import Provision

PROVISIONS = [
    Provision(id="cpc_1908:s9", statute_id="cpc_1908", section="9", blueprint_topic="jurisdiction of civil courts (blueprint)"),
]
