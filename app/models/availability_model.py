
"""Database operations for maid availability management."""

from app.database import fetch_all, fetch_one, execute_query



def get_maid_availability(maid_id):
    """Return availability slots with JSON-friendly time strings."""
    query = """
        SELECT
            availability_id,
            maid_id,
            day_of_week,
            start_time,
            end_time,
            status
        FROM maid_availability
        WHERE maid_id = %s
        ORDER BY day_of_week, start_time
    """

    slots = fetch_all(query, (maid_id,))

    # MySQL TIME values may be returned as timedelta objects.
    # Convert them into strings so Flask can serialize the response.
    for slot in slots:
        for field in ("start_time", "end_time"):
            value = slot[field]

            if hasattr(value, "total_seconds"):
                total_seconds = int(value.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                slot[field] = (
                    f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                )
            else:
                slot[field] = str(value)

    return slots



def add_maid_availability(maid_id, day_of_week, start_time, end_time):
    """Add a new availability slot after validating its values."""

    if not isinstance(day_of_week, int) or isinstance(day_of_week, bool):
        return False, "Invalid day of week."

    if not 1 <= day_of_week <= 7:
        return False, "Day must be between Monday (1) and Sunday (7)."

    if start_time >= end_time:
        return False, "End time must be later than start time."

    # Prevent overlapping active slots on the same day.
    overlap_query = """
        SELECT availability_id
        FROM maid_availability
        WHERE maid_id = %s
          AND day_of_week = %s
          AND status = 'ACTIVE'
          AND start_time < %s
          AND end_time > %s
        LIMIT 1
    """
    overlap = fetch_one(
        overlap_query,
        (maid_id, day_of_week, end_time, start_time)
    )

    if overlap:
        return False, "This slot overlaps an existing active slot."

    insert_query = """
        INSERT INTO maid_availability
            (maid_id, day_of_week, start_time, end_time, status)
        VALUES (%s, %s, %s, %s, 'ACTIVE')
    """

    try:
        execute_query(
            insert_query,
            (maid_id, day_of_week, start_time, end_time)
        )
        return True, "Availability added successfully."
    except Exception:
        return False, "Unable to add availability."


def update_maid_availability_status(maid_id, availability_id, status):
    """Activate or deactivate a slot owned by the logged-in maid."""

    if status not in ("ACTIVE", "INACTIVE"):
        return False, "Invalid availability status."

    query = """
        UPDATE maid_availability
        SET status = %s
        WHERE availability_id = %s
          AND maid_id = %s
    """

    try:
        execute_query(query, (status, availability_id, maid_id))

        # Verify that the requested slot belongs to this maid.
        check_query = """
            SELECT availability_id
            FROM maid_availability
            WHERE availability_id = %s AND maid_id = %s
        """
        existing = fetch_one(check_query, (availability_id, maid_id))

        if not existing:
            return False, "Availability slot not found."

        return True, "Availability status updated successfully."
    except Exception:
        return False, "Unable to update availability status."
