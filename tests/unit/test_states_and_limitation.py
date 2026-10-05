import itertools
import pytest

from app.domain.states import EvalState as S, combine_all
from app.engines import limitation_engine

ORDER = [S.NOT_SATISFIED, S.DISPUTED, S.UNKNOWN, S.REQUIRES_LAWYER_JUDGMENT, S.SATISFIED]


def test_precedence_pairs():
    for i, a in enumerate(ORDER):
        for b in ORDER[i:]:
            assert combine_all([a, b]) == a
            assert combine_all([b, a]) == a


def test_not_applicable_skipped_and_all_na():
    assert combine_all([S.NOT_APPLICABLE, S.SATISFIED]) == S.SATISFIED
    assert combine_all([S.NOT_APPLICABLE]) == S.NOT_APPLICABLE
    assert combine_all([]) == S.NOT_APPLICABLE


def test_unknown_beats_judgment():
    assert combine_all([S.REQUIRES_LAWYER_JUDGMENT, S.UNKNOWN]) == S.UNKNOWN


RULE = {"id": "T", "authoring_status": "DRAFT_UNVERIFIED", "period_days": 90}


def test_limitation_missing_dates_are_unknown_never_within_time():
    assert limitation_engine.evaluate(RULE, None, "2026-02-01").state == S.UNKNOWN
    assert limitation_engine.evaluate(RULE, "2026-01-01", None).state == S.UNKNOWN
    assert limitation_engine.evaluate(RULE, "garbage", "2026-02-01").state == S.UNKNOWN


def test_limitation_boundaries():
    assert limitation_engine.evaluate(RULE, "2026-01-01", "2026-04-01").state == S.SATISFIED   # day 90
    assert limitation_engine.evaluate(RULE, "2026-01-01", "2026-04-02").state == S.NOT_SATISFIED  # day 91
    assert limitation_engine.evaluate(RULE, "2026-01-01", "2026-04-02", exclusion_days=1).state == S.SATISFIED


def test_pending_rule_is_unknown_even_with_dates():
    pending = {"id": "P", "authoring_status": "PENDING", "period_days": None}
    assert limitation_engine.evaluate(pending, "2026-01-01", "2026-01-02").state == S.UNKNOWN
