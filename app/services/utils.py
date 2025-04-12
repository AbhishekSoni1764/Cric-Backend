from datetime import datetime


def clean_null_values(data: dict) -> dict:
    """Remove null values from a dictionary."""
    return {k: v for k, v in data.items() if v is not None}


def get_current_timestamp() -> str:
    """Return current UTC timestamp as string."""
    return datetime.utcnow().isoformat()
