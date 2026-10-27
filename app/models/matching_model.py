# app/models/matching_model.py
# Rule-based shortlist queries for Admin review.
# Weekdays in requirement_schedules are names; maid_availability uses 1=Monday ... 7=Sunday.

import re
from datetime import time, timedelta

from app.database import fetch_one, fetch_all

DAY_TO_NUMBER = {
    "MONDAY": 1,
    "TUESDAY": 2,
    "WEDNESDAY": 3,
    "THURSDAY": 4,
    "FRIDAY": 5,
    "SATURDAY": 6,
    "SUNDAY": 7,
}

# Assignments in these states reserve the maid's weekly schedule.
BLOCKING_ASSIGNMENT_STATUSES = (
    "PENDING_MAID_RESPONSE",
    "MAID_ACCEPTED",
    "CUSTOMER_CONFIRMED",
    "ADMIN_CONFIRMED",
)


def get_requirement_for_matching(requirement_id):
    """Return a requirement only when it is ready for Admin matching."""
    return fetch_one(
        """
        SELECT requirement_id, customer_id, city, pincode,
               experience_requirement, status
        FROM household_requirements
        WHERE requirement_id = %s
          AND status IN ('SUBMITTED', 'UNDER_REVIEW')
        """,
        (requirement_id,),
    )


def get_required_service_ids(requirement_id):
    """Get all service IDs requested for the household."""
    rows = fetch_all(
        """
        SELECT service_id
        FROM requirement_services
        WHERE requirement_id = %s
        ORDER BY service_id
        """,
        (requirement_id,),
    )
    return [int(row["service_id"]) for row in rows]


def get_required_schedules(requirement_id):
    """Get the household's saved weekly schedule."""
    return fetch_all(
        """
        SELECT day_of_week, start_time, end_time
        FROM requirement_schedules
        WHERE requirement_id = %s
        ORDER BY FIELD(
            day_of_week,
            'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY',
            'FRIDAY', 'SATURDAY', 'SUNDAY'
        ), start_time
        """,
        (requirement_id,),
    )


def _time_to_seconds(value):
    """Normalize MySQL TIME values to seconds after midnight."""
    if isinstance(value, timedelta):
        return int(value.total_seconds())
    if isinstance(value, time):
        return value.hour * 3600 + value.minute * 60 + value.second
    text = str(value).strip()
    parts = text.split(":")
    if len(parts) not in (2, 3):
        raise ValueError(f"Unsupported time value: {value!r}")
    hour, minute = int(parts[0]), int(parts[1])
    second = int(parts[2]) if len(parts) == 3 else 0
    return hour * 3600 + minute * 60 + second


def _weekday_number(value):
    """Translate a stored weekday name to the availability table's number."""
    if isinstance(value, int):
        if 1 <= value <= 7:
            return value
        raise ValueError(f"Invalid weekday number: {value}")
    day = str(value).strip().upper()
    if day in DAY_TO_NUMBER:
        return DAY_TO_NUMBER[day]
    # Tolerate numeric strings in case older test data used them.
    if day.isdigit() and 1 <= int(day) <= 7:
        return int(day)
    raise ValueError(f"Unsupported weekday value: {value!r}")


def _candidate_supports_schedule(maid_id, required_schedules):
    """Require one active availability interval to cover each requested interval."""
    availability = fetch_all(
        """
        SELECT day_of_week, start_time, end_time
        FROM maid_availability
        WHERE maid_id = %s AND status = 'ACTIVE'
        """,
        (maid_id,),
    )

    by_day = {}
    for row in availability:
        day = _weekday_number(row["day_of_week"])
        by_day.setdefault(day, []).append(
            (_time_to_seconds(row["start_time"]),
             _time_to_seconds(row["end_time"]))
        )

    for schedule in required_schedules:
        day = _weekday_number(schedule["day_of_week"])
        start = _time_to_seconds(schedule["start_time"])
        end = _time_to_seconds(schedule["end_time"])
        # A single availability row must fully cover the requested interval.
        if not any(
            available_start <= start and available_end >= end
            for available_start, available_end in by_day.get(day, [])
        ):
            return False
    return True


def _candidate_has_assignment_conflict(maid_id, requirement_id, required_schedules):
    """Exclude a maid when a non-finalized assignment overlaps a requested time."""
    rows = fetch_all(
        """
        SELECT rs.day_of_week, rs.start_time, rs.end_time
        FROM maid_assignments ma
        JOIN requirement_schedules rs
          ON rs.requirement_id = ma.requirement_id
        WHERE ma.maid_id = %s
          AND ma.requirement_id <> %s
          AND ma.status IN (
              'PENDING_MAID_RESPONSE',
              'MAID_ACCEPTED',
              'CUSTOMER_CONFIRMED',
              'ADMIN_CONFIRMED'
          )
        """,
        (maid_id, requirement_id),
    )

    existing_by_day = {}
    for row in rows:
        day = _weekday_number(row["day_of_week"])
        existing_by_day.setdefault(day, []).append(
            (_time_to_seconds(row["start_time"]),
             _time_to_seconds(row["end_time"]))
        )

    for schedule in required_schedules:
        day = _weekday_number(schedule["day_of_week"])
        start = _time_to_seconds(schedule["start_time"])
        end = _time_to_seconds(schedule["end_time"])
        for existing_start, existing_end in existing_by_day.get(day, []):
            # Half-open intervals: back-to-back appointments are allowed.
            if start < existing_end and existing_start < end:
                return True
    return False


def _experience_requirement_years(value):
    """Extract a numeric year threshold when the requirement clearly states one."""
    if value is None:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)", str(value))
    return float(match.group(1)) if match else None


def get_service_matched_maids(service_ids, city=None, pincode=None):
    """
    Return active, complete, verified maids supporting every requested service.
    Availability and assignment conflicts are checked by get_maid_shortlist().
    """
    service_ids = sorted(set(int(service_id) for service_id in (service_ids or [])))
    if not service_ids:
        return []

    placeholders = ", ".join(["%s"] * len(service_ids))
    return fetch_all(
        f"""
        SELECT
            mp.maid_id,
            u.full_name,
            mp.experience_years,
            mp.city,
            mp.pincode,
            COUNT(DISTINCT ms.service_id) AS matched_service_count
        FROM maid_profiles mp
        JOIN users u ON u.user_id = mp.maid_id
        JOIN maid_services ms ON ms.maid_id = mp.maid_id
        WHERE u.role = 'MAID'
          AND u.status = 'ACTIVE'
          AND mp.profile_status = 'COMPLETE'
          AND ms.service_id IN ({placeholders})
          AND (
              SELECT mv.status
              FROM maid_verifications mv
              WHERE mv.maid_id = mp.maid_id
              ORDER BY mv.verification_id DESC
              LIMIT 1
          ) = 'VERIFIED'
        GROUP BY mp.maid_id, u.full_name, mp.experience_years, mp.city, mp.pincode
        HAVING COUNT(DISTINCT ms.service_id) = %s
        """,
        (*service_ids, len(service_ids)),
    )


def get_maid_shortlist(requirement_id):
    """
    Return a transparent, ranked shortlist for an Admin.
    Returns (requirement, candidates, message). No assignment is created here.
    """
    requirement = get_requirement_for_matching(requirement_id)
    if not requirement:
        return None, [], (
            "Requirement was not found or is not SUBMITTED/UNDER_REVIEW. "
            "Only submitted requirements can be shortlisted."
        )

    service_ids = get_required_service_ids(requirement_id)
    schedules = get_required_schedules(requirement_id)
    if not service_ids or not schedules:
        return requirement, [], "The requirement has no saved services or schedules."

    candidates = get_service_matched_maids(
        service_ids,
        requirement.get("city"),
        requirement.get("pincode"),
    )

    minimum_experience = _experience_requirement_years(
        requirement.get("experience_requirement")
    )
    shortlist = []

    for candidate in candidates:
        maid_id = int(candidate["maid_id"])
        candidate["experience_years"] = float(candidate.get("experience_years") or 0)
        # Apply an experience threshold only when the saved value is numeric
        # or contains a numeric year value.
        if (
            minimum_experience is not None
            and float(candidate.get("experience_years") or 0) < minimum_experience
        ):
            continue
        if not _candidate_supports_schedule(maid_id, schedules):
            continue
        if _candidate_has_assignment_conflict(maid_id, requirement_id, schedules):
            continue

        same_city = bool(
            requirement.get("city")
            and candidate.get("city")
            and str(requirement["city"]).strip().casefold()
            == str(candidate["city"]).strip().casefold()
        )
        same_pincode = bool(
            requirement.get("pincode")
            and candidate.get("pincode")
            and str(requirement["pincode"]).strip()
            == str(candidate["pincode"]).strip()
        )

        # Higher score is better; these are transparent rule-based points.
        score = (
            (50 if same_pincode else 0)
            + (25 if same_city else 0)
            + min(float(candidate.get("experience_years") or 0), 20)
        )
        candidate["same_pincode"] = same_pincode
        candidate["same_city"] = same_city
        candidate["shortlist_score"] = round(score, 2)
        candidate["match_reasons"] = [
            "All requested services supported",
            "Verified and active",
            "Availability covers requested schedule",
            "No overlapping active or pending assignment",
        ]
        if same_pincode:
            candidate["match_reasons"].append("Same pincode")
        elif same_city:
            candidate["match_reasons"].append("Same city")
        shortlist.append(candidate)

    shortlist.sort(
        key=lambda item: (
            -item["shortlist_score"],
            -float(item.get("experience_years") or 0),
            int(item["maid_id"]),
        )
    )
    message = (
        "Eligible candidates found."
        if shortlist
        else "No eligible maid currently matches all service, schedule, and conflict rules."
    )
    return requirement, shortlist, message
