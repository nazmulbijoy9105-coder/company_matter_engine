class EngineError(Exception):
    """Base class for engine errors."""


class GateBlocked(EngineError):
    """A workflow gate refused the transition."""


class VerificationError(EngineError):
    """Something claimed VERIFIED without the required attestation."""


class UnknownReference(EngineError):
    """A rule or taxonomy id does not resolve."""
