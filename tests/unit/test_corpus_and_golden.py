from pathlib import Path
import pytest

from app.core.errors import VerificationError
from app.legal.corpus.models import Provision, Statute, VerificationStatus
from app.legal.corpus.registries import provision_registry, section_registry
from app.engines import pipeline
from tools import validate_legal_corpus
from tools.run_golden import check, load_case

ROOT = Path(__file__).resolve().parents[2]
CASES = sorted((ROOT / "tests" / "golden_cases").rglob("*.json"))


def test_corpus_validator_clean():
    assert validate_legal_corpus.run() == []


def test_nothing_in_shipped_corpus_is_verified():
    assert all(p.verification_status != VerificationStatus.VERIFIED for p in provision_registry().values())
    assert all(p.text is None for p in provision_registry().values())


def test_verified_requires_attestation():
    with pytest.raises(VerificationError):
        Provision(id="x", statute_id="s", section="1", verification_status=VerificationStatus.VERIFIED)
    with pytest.raises(VerificationError):
        Provision(id="x", statute_id="s", section="1", text="made up text")
    with pytest.raises(VerificationError):
        Statute(id="s", title="t", year=1, verification_status=VerificationStatus.VERIFIED, verified_by="a")


def test_section_registry_links_hook_to_everything():
    info = section_registry()["HOOK-CA-233"]
    assert "RS-CA-233" in info["rule_sets"] and "REM-005" in info["remedies"]
    assert "CM-021" in info["matter_types"] and "EV-CORP-006" in info["required_evidence"]
    assert section_registry()["HOOK-CA-195"]["provisions"] == ["companies_act_1994:s195"]


@pytest.mark.parametrize("path", CASES, ids=[p.parent.name + "/" + p.stem for p in CASES])
def test_golden(path):
    spec, matter, book = load_case(path)
    assert check(spec, pipeline.run(matter, book)) == []


def test_label_never_changes_outcome():
    from app.domain.matter import Matter
    from app.engines import jurisdiction_engine
    a = Matter(matter_id="a", claimed_label="company matter", requested_relief=["REM-900"])
    b = Matter(matter_id="b", claimed_label=None, requested_relief=["REM-900"])
    assert jurisdiction_engine.screen(a).outcome == jurisdiction_engine.screen(b).outcome


def test_classifier_does_not_pick_primary_on_tie():
    from app.domain.matter import Matter
    from app.engines.matter_classifier import classify
    c = classify(Matter(matter_id="m", invoked_hooks=["HOOK-CA-233", "HOOK-CA-195"]))
    assert c.primary is None and c.needs_reviewer_choice
    c2 = classify(Matter(matter_id="m", invoked_hooks=["HOOK-CA-233", "HOOK-CA-195"], proposed_matter_types=["CM-022"]))
    assert c2.primary == "CM-022"
