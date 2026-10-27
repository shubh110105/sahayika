
from datetime import datetime



from app.models.requirement_model import (
    create_requirement_with_details,
    get_customer_requirements,
    get_service_pricing,
    save_requirement_salary_estimate,
    get_requirement_services,   # Retrieve the requirement's saved services.
    get_requirement_schedules,  # Retrieve its saved weekly schedule.
)


from app.database import fetch_one


VALID_DAYS = {
    "MONDAY",
    "TUESDAY",
    "WEDNESDAY",
    "THURSDAY",
    "FRIDAY",
    "SATURDAY",
    "SUNDAY",
}


def create_household_requirement(
    customer_id,
    location_address,
    city,
    state,
    pincode,
    experience_requirement,
    additional_requirements,
    service_ids,
    schedules,
):
    location_address = (location_address or "").strip()
    city = (city or "").strip()
    state = (state or "").strip()
    pincode = (pincode or "").strip()
    additional_requirements = (
        additional_requirements or ""
    ).strip()

    if not location_address:
        return False, "Household address is required."

    if not city:
        return False, "City is required."

    if not state:
        return False, "State is required."

    if not pincode:
        return False, "Pincode is required."

    if not pincode.isdigit() or len(pincode) != 6:
        return False, "Enter a valid 6-digit pincode."

    if not isinstance(service_ids, list) or not service_ids:
        return False, "Select at least one service."

    try:
        service_ids = [int(service_id) for service_id in service_ids]
    except (TypeError, ValueError):
        return False, "Invalid service selection."

    if any(service_id <= 0 for service_id in service_ids):
        return False, "Invalid service selection."

    if len(service_ids) != len(set(service_ids)):
        return False, "Duplicate services are not allowed."

    if not isinstance(schedules, list) or not schedules:
        return False, "Add at least one weekly schedule."


    for schedule in schedules:
        if not isinstance(schedule, dict):
            return False, "Invalid schedule format."

        day = str(schedule.get("day_of_week", "")).strip().upper()

        start = schedule.get("start_time", "")
        end = schedule.get("end_time", "")

        if day not in VALID_DAYS:
            return False, "Select a valid weekday."

        try:
            start_time = datetime.strptime(start, "%H:%M").time()
            end_time = datetime.strptime(end, "%H:%M").time()
        except (TypeError, ValueError):
            return False, "Enter valid start and end times in HH:MM format."

        if start_time >= end_time:
            return False, "End time must be later than start time."


    # Confirm the customer profile exists.
    customer = fetch_one(
        """
        SELECT customer_id
        FROM customer_profiles
        WHERE customer_id = %s
        """,
        (customer_id,),
    )

    if not customer:
        return False, "Complete your customer profile first."

    # Confirm every requested service exists.
    placeholders = ", ".join(["%s"] * len(service_ids))
    services = fetch_one(
        f"""
        SELECT COUNT(*) AS service_count
        FROM services
        WHERE service_id IN ({placeholders})
        """,
        tuple(service_ids),
    )

    if services["service_count"] != len(service_ids):
        return False, "One or more selected services do not exist."

    
    normalized_schedules = [
        {
            "day_of_week": str(s["day_of_week"]).strip().upper(),
            "start_time": s["start_time"],
            "end_time": s["end_time"],
        }
        for s in schedules
    ]

    # Calculate the estimate before creating the requirement.
    estimate_success, estimate_result = estimate_monthly_salary(
        service_ids,
        normalized_schedules,
    )

    if not estimate_success:
        return False, estimate_result

    requirement_id = create_requirement_with_details(
        customer_id=customer_id,
        location_address=location_address,
        city=city,
        state=state,
        pincode=pincode,
        experience_requirement=experience_requirement,
        additional_requirements=additional_requirements or None,
        service_ids=service_ids,
        schedules=normalized_schedules,
    )

    save_requirement_salary_estimate(
        requirement_id,
        estimate_result["estimated_monthly_salary"],
    )

    return True, requirement_id


def list_customer_requirements(customer_id):
    return get_customer_requirements(customer_id)


def estimate_monthly_salary(service_ids, schedules):
    """
    Estimate monthly salary using configured service rates.

    Baseline:
    - Rates cover up to 1 hour per visit.
    - Standard frequency is 6 days per week.
    - A month is approximated as 52 / 12 weeks.
    """

    if not service_ids or not schedules:
        return False, "Services and schedules are required."

    try:
        service_ids = list(set(int(sid) for sid in service_ids))
    except (TypeError, ValueError):
        return False, "Invalid service selection."

    if any(sid <= 0 for sid in service_ids):
        return False, "Invalid service selection."

    # Merge overlapping schedule intervals on each weekday.
    daily_intervals = {}

    try:
        for schedule in schedules:
            day = str(schedule["day_of_week"]).strip().upper()
            start = datetime.strptime(
                schedule["start_time"], "%H:%M"
            )
            end = datetime.strptime(
                schedule["end_time"], "%H:%M"
            )

            if day not in VALID_DAYS or start >= end:
                return False, "Invalid schedule."

            daily_intervals.setdefault(day, []).append(
                (start, end)
            )
    except (KeyError, TypeError, ValueError):
        return False, "Invalid schedule format."

    daily_hours = {}

    for day, intervals in daily_intervals.items():
        intervals.sort(key=lambda interval: interval[0])

        merged = []
        for start, end in intervals:
            if not merged or start > merged[-1][1]:
                merged.append([start, end])
            elif end > merged[-1][1]:
                merged[-1][1] = end

        total_hours = sum(
            (end - start).total_seconds() / 3600
            for start, end in merged
        )
        daily_hours[day] = total_hours

    working_days = len(daily_hours)

    if working_days > 7:
        return False, "Invalid number of working days."

    pricing_rows = get_service_pricing(service_ids)

    prices_by_id = {
        int(row["service_id"]): row
        for row in pricing_rows
    }

    missing_ids = set(service_ids) - set(prices_by_id)
    if missing_ids:
        return False, (
            "Active pricing is missing for one or more "
            "selected services."
        )

    weeks_per_month = 52 / 12
    estimated_total = 0.0
    breakdown = []

    # Extra hours are calculated beyond one hour per visit.
    extra_hours_per_week = sum(
        max(0, hours - 1)
        for hours in daily_hours.values()
    )

    for service_id in service_ids:
        price = prices_by_id[service_id]

        base_rate = float(price["base_monthly_rate"])
        extra_hour_rate = float(price["rate_per_extra_hour"])

        frequency_cost = base_rate * working_days / 6

        extra_hours_cost = (
            extra_hour_rate
            * extra_hours_per_week
            * weeks_per_month
        )

        service_total = frequency_cost + extra_hours_cost
        estimated_total += service_total

        breakdown.append({
            "service_id": service_id,
            "service_name": price["service_name"],
            "base_rate": round(base_rate, 2),
            "frequency_cost": round(frequency_cost, 2),
            "extra_hours_cost": round(extra_hours_cost, 2),
            "estimated_monthly_cost": round(service_total, 2),
        })

    return True, {
        "estimated_monthly_salary": round(estimated_total, 2),
        "working_days_per_week": working_days,
        "breakdown": breakdown,
    }

def reassess_requirement_salary(requirement_id):
    """Recalculate and save salary for an Admin-requested reassessment."""

    # Only process requirements explicitly marked for reassessment.
    requirement = fetch_one(
        """
        SELECT requirement_id
        FROM household_requirements
        WHERE requirement_id = %s
          AND status = 'SALARY_REVIEW_REQUESTED'
          AND salary_review_decision = 'REASSESSMENT_REQUESTED'
        """,
        (requirement_id,),
    )

    if not requirement:
        return False, "This requirement is not awaiting reassessment."

    # Load the services and schedule originally submitted by the customer.
    service_rows = get_requirement_services(requirement_id)
    schedule_rows = get_requirement_schedules(requirement_id)

    if not service_rows or not schedule_rows:
        return False, "Saved services or schedule are missing."

    # Extract service IDs and normalize database time values to HH:MM.
    service_ids = [int(row["service_id"]) for row in service_rows]

    
    def normalize_time(value):
        # MySQL TIME values may be returned as timedelta objects.
        if hasattr(value, "total_seconds"):
            total_seconds = int(value.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60

            # Always produce zero-padded HH:MM, such as 09:00.
            return f"{hours:02d}:{minutes:02d}"

        # Python time objects can format themselves directly.
        if hasattr(value, "strftime"):
            return value.strftime("%H:%M")

        # Accept strings with or without seconds.
        text = str(value).strip()

        for time_format in ("%H:%M", "%H:%M:%S"):
            try:
                return datetime.strptime(
                    text, time_format
                ).strftime("%H:%M")
            except ValueError:
                continue

        # Reject values that cannot safely be interpreted as times.
        raise ValueError("Invalid saved schedule time.")

    try:
        # Convert database rows into the format expected by the calculator.
        schedules = [
            {
                "day_of_week": str(row["day_of_week"]).upper(),
                "start_time": normalize_time(row["start_time"]),
                "end_time": normalize_time(row["end_time"]),
            }
            for row in schedule_rows
        ]
    except (KeyError, TypeError, ValueError):
        return False, "Unable to read the saved schedule times."


    # Reuse the existing salary calculator instead of duplicating its logic.
    success, result = estimate_monthly_salary(service_ids, schedules)
 
    if not success:
        return False, result

    # Save the recalculated amount and reset the review status.
    estimated_salary = result["estimated_monthly_salary"]

    save_requirement_salary_estimate(
        requirement_id,
        estimated_salary,
    )

    # Verify the update because execute_query's return value is not a
    # reliable indicator of whether an UPDATE affected a database row.
    saved_requirement = fetch_one(
        """
        SELECT requirement_id
        FROM household_requirements
        WHERE requirement_id = %s
          AND status = 'SALARY_ESTIMATED'
          AND salary_review_decision = 'PENDING'
          AND estimated_monthly_salary = %s
        """,
        (requirement_id, estimated_salary),
    )

    if not saved_requirement:
        return False, "Unable to save the reassessed salary."

    return True, {
        "requirement_id": requirement_id,
        "estimated_monthly_salary": estimated_salary,
        "message": "Salary reassessed and saved successfully.",
    }
