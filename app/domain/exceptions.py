class DomainError(Exception):
    """Kesalahan generik domain."""


class InvalidStateTransition(DomainError):
    """Dilempar saat perubahan status tidak valid."""
