"""Lists every precedent with its verification gaps. Run: python -m tools.audit_precedent_registry"""
from app.precedent.registry import PrecedentRegistry
from app.precedent.verification import verification_gaps

if __name__ == "__main__":
    reg = PrecedentRegistry.load()
    if not reg.all():
        print("precedent registry is empty: Law-Only mode only")
    for r in reg.all():
        print(r.precedent_id, r.status, verification_gaps(r) or "")
