class KaggleManagerError(Exception):
    """Base class for KaggleManager exceptions."""

class KaggleAuthenticationError(KaggleManagerError):
    """Raised when authentication with Kaggle API fails."""
