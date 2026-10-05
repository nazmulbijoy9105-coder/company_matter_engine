"""Run: python -m tools.audit_maintainability"""
import sys

from tools.validate_legal_corpus import main

if __name__ == "__main__":
    sys.exit(main(['maintainability']))
