
from datetime import datetime

from app.models.requirement_model import (
    create_requirement_with_details,
    get_customer_requirements,
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

    requirement_id = create_requirement_with_details(
        customer_id=customer_id,
        location_address=location_address,
        city=city,
        state=state,
        pincode=pincode,
        experience_requirement=experience_requirement,
        additional_requirements=additional_requirements or None,
        service_ids=service_ids,
        schedules=[
            {
                "day_of_week": str(s["day_of_week"]).upper(),
                "start_time": s["start_time"],
                "end_time": s["end_time"],
            }
            for s in schedules
        ],
    )

    return True, requirement_id


def list_customer_requirements(customer_id):
    return get_customer_requirements(customer_id)
