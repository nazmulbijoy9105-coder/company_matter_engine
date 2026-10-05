"""Run: python -m tools.audit_evidence_mapping"""
import sys

from tools.validate_legal_corpus import main

if __name__ == "__main__":
    sys.exit(main(['evidence']))
