from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

def retrieve_account_age(activated_at) -> str:
    """Takes the activated ISO timestamp from the faceit API and retrieves the account's age.

    Args:
        activated_at (str): ISO timestamp associated with the account's age.

    Returns:
        str: Number of years, months and days since the account's activation.
    """
    current_timestamp = datetime.now(timezone.utc)
    activated_timestamp = datetime.fromisoformat(activated_at)
    time_difference = relativedelta(current_timestamp, activated_timestamp)
    return (
        f"{time_difference.years} years, "
        f"{time_difference.months} months, "
        f"{time_difference.days} days"
    )
