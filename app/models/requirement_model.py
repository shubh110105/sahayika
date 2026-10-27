
from app.database import (
    fetch_one,
    fetch_all,
    execute_query,
    execute_transaction
)

def create_requirement(
    customer_id,
    location_address,
    city,
    state,
    pincode,
    experience_requirement,
    additional_requirements
):
    query = """
        INSERT INTO household_requirements (
            customer_id,
            location_address,
            city,
            state,
            pincode,
            experience_requirement,
            additional_requirements,
            status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'DRAFT')
    """

    return execute_query(
        query,
        (
            customer_id,
            location_address,
            city,
            state,
            pincode,
            experience_requirement,
            additional_requirements
        )
    )


def add_requirement_services(requirement_id, service_ids):
    query = """
        INSERT INTO requirement_services (
            requirement_id,
            service_id
        )
        VALUES (%s, %s)
    """

    for service_id in service_ids:
        execute_query(query, (requirement_id, service_id))


def add_requirement_schedule(
    requirement_id,
    day_of_week,
    start_time,
    end_time
):
    query = """
        INSERT INTO requirement_schedules (
            requirement_id,
            day_of_week,
            start_time,
            end_time
        )
        VALUES (%s, %s, %s, %s)
    """

    return execute_query(
        query,
        (
            requirement_id,
            day_of_week,
            start_time,
            end_time
        )
    )


def get_requirement_by_id(requirement_id, customer_id):
    query = """
        SELECT
            requirement_id,
            customer_id,
            location_address,
            city,
            state,
            pincode,
            experience_requirement,
            additional_requirements,
            status,
            estimated_monthly_salary,
            salary_estimated_at,
            created_at,
            updated_at
        FROM household_requirements
        WHERE requirement_id = %s
          AND customer_id = %s
    """

    return fetch_one(query, (requirement_id, customer_id))


def get_customer_requirements(customer_id):
    query = """
        SELECT
            requirement_id,
            location_address,
            city,
            state,
            pincode,
            experience_requirement,
            status,
            created_at
        FROM household_requirements
        WHERE customer_id = %s
        ORDER BY created_at DESC
    """

    return fetch_all(query, (customer_id,))



def create_requirement_with_details(
    customer_id,
    location_address,
    city,
    state,
    pincode,
    experience_requirement,
    additional_requirements,
    service_ids,
    schedules
):
    def operation(cursor):
        cursor.execute(
            """
            INSERT INTO household_requirements (
                customer_id,
                location_address,
                city,
                state,
                pincode,
                experience_requirement,
                additional_requirements,
                status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'DRAFT')
            """,
            (
                customer_id,
                location_address,
                city,
                state,
                pincode,
                experience_requirement,
                additional_requirements
            )
        )

        requirement_id = cursor.lastrowid

        for service_id in service_ids:
            cursor.execute(
                """
                INSERT INTO requirement_services (
                    requirement_id,
                    service_id
                )
                VALUES (%s, %s)
                """,
                (requirement_id, service_id)
            )

        for schedule in schedules:
            cursor.execute(
                """
                INSERT INTO requirement_schedules (
                    requirement_id,
                    day_of_week,
                    start_time,
                    end_time
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    requirement_id,
                    schedule["day_of_week"],
                    schedule["start_time"],
                    schedule["end_time"]
                )
            )

        return requirement_id

    return execute_transaction(operation)


def get_all_services():
    query = """
        SELECT service_id, service_name
        FROM services
        ORDER BY service_name ASC
    """
    return fetch_all(query)


def get_requirement_services(requirement_id):
    query = """
        SELECT s.service_id, s.service_name
        FROM requirement_services rs
        JOIN services s ON s.service_id = rs.service_id
        WHERE rs.requirement_id = %s
        ORDER BY s.service_name
    """
    return fetch_all(query, (requirement_id,))


def get_requirement_schedules(requirement_id):
    query = """
        SELECT day_of_week, start_time, end_time
        FROM requirement_schedules
        WHERE requirement_id = %s
        ORDER BY FIELD(
            day_of_week,
            'MONDAY', 'TUESDAY', 'WEDNESDAY',
            'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'
        ), start_time
    """
    return fetch_all(query, (requirement_id,))


def get_service_pricing(service_ids):
    if not service_ids:
        return []

    placeholders = ", ".join(["%s"] * len(service_ids))

    query = f"""
        SELECT
            s.service_id,
            s.service_name,
            sp.base_monthly_rate,
            sp.rate_per_extra_hour
        FROM service_pricing sp
        JOIN services s
            ON s.service_id = sp.service_id
        WHERE s.service_id IN ({placeholders})
          AND sp.is_active = 'ACTIVE'
        ORDER BY s.service_name
    """

    return fetch_all(query, tuple(service_ids))


def save_requirement_salary_estimate(requirement_id, estimated_salary):
    # Update the latest salary estimate and its timestamp.
    # The existing status rules are preserved.
    def operation(cursor):
        cursor.execute(
            """
            UPDATE household_requirements
            SET
                estimated_monthly_salary = %s,
                salary_estimated_at = CURRENT_TIMESTAMP,
                status = 'SALARY_ESTIMATED',
                salary_review_decision = 'PENDING'
            WHERE requirement_id = %s
              AND status IN ('DRAFT', 'SALARY_REVIEW_REQUESTED')
            """,
            (estimated_salary, requirement_id)
        )

        # Stop if the requirement was not eligible for an update.
        if cursor.rowcount != 1:
            raise ValueError(
                "Requirement was not found or is not eligible for salary estimation."
            )

        # Mark the previous estimate as historical, not current.
        cursor.execute(
            """
            UPDATE salary_estimates
            SET is_current = FALSE
            WHERE requirement_id = %s
              AND is_current = TRUE
            """,
            (requirement_id,)
        )

        # Insert the new estimate as the current estimate.
        cursor.execute(
            """
            INSERT INTO salary_estimates (
                requirement_id,
                estimated_amount,
                calculation_version,
                is_current
            )
            VALUES (%s, %s, %s, TRUE)
            """,
            (requirement_id, estimated_salary, "v1")
        )

        # Return success; execute_transaction commits both changes together.
        return True

    # Run all database changes in one transaction to prevent partial updates.
    return execute_transaction(operation)



def request_salary_review(requirement_id, customer_id):
    query = """
        UPDATE household_requirements
        SET status = 'SALARY_REVIEW_REQUESTED'
        WHERE requirement_id = %s
          AND customer_id = %s
          AND status = 'SALARY_ESTIMATED'
          AND estimated_monthly_salary IS NOT NULL
    """

    execute_query(query, (requirement_id, customer_id))

    updated_requirement = fetch_one(
        """
        SELECT requirement_id
        FROM household_requirements
        WHERE requirement_id = %s
          AND customer_id = %s
          AND status = 'SALARY_REVIEW_REQUESTED'
        """,
        (requirement_id, customer_id)
    )

    return updated_requirement is not None


def cancel_household_requirement(requirement_id, customer_id):
    query = """
        UPDATE household_requirements
        SET status = 'CANCELLED'
        WHERE requirement_id = %s
          AND customer_id = %s
          AND status IN (
              'DRAFT',
              'SALARY_ESTIMATED',
              'SALARY_REVIEW_REQUESTED',
              'SUBMITTED',
              'UNDER_REVIEW',
              'NO_MATCH_AVAILABLE'
          )
    """

    execute_query(query, (requirement_id, customer_id))

    cancelled_requirement = fetch_one(
        """
        SELECT requirement_id
        FROM household_requirements
        WHERE requirement_id = %s
          AND customer_id = %s
          AND status = 'CANCELLED'
        """,
        (requirement_id, customer_id)
    )

    return cancelled_requirement is not None


def get_salary_review_requests():
    query = """
        SELECT
            hr.requirement_id,
            hr.customer_id,
            hr.location_address,
            hr.city,
            hr.state,
            hr.pincode,
            hr.estimated_monthly_salary,
            hr.salary_estimated_at,
            hr.status,
            hr.salary_review_decision,
            hr.created_at
        FROM household_requirements AS hr
        WHERE hr.status = 'SALARY_REVIEW_REQUESTED'
          AND hr.salary_review_decision = 'PENDING'
        ORDER BY hr.salary_estimated_at ASC
    """
    return fetch_all(query)


def update_salary_review_decision(requirement_id, decision):
    allowed_decisions = {
        "APPROVED",
        "REASSESSMENT_REQUESTED"
    }

    if decision not in allowed_decisions:
        return False

    if decision == "APPROVED":
        query = """
            UPDATE household_requirements
            SET salary_review_decision = %s,
                status = 'SALARY_ESTIMATED'
            WHERE requirement_id = %s
              AND status = 'SALARY_REVIEW_REQUESTED'
              AND salary_review_decision = 'PENDING'
        """
    else:
        query = """
            UPDATE household_requirements
            SET salary_review_decision = %s
            WHERE requirement_id = %s
              AND status = 'SALARY_REVIEW_REQUESTED'
              AND salary_review_decision = 'PENDING'
        """

    execute_query(query, (decision, requirement_id))

    updated_requirement = fetch_one(
        """
        SELECT requirement_id
        FROM household_requirements
        WHERE requirement_id = %s
          AND salary_review_decision = %s
          AND (
              (status = 'SALARY_ESTIMATED' AND %s = 'APPROVED')
              OR
              (status = 'SALARY_REVIEW_REQUESTED'
               AND %s = 'REASSESSMENT_REQUESTED')
          )
        """,
        (requirement_id, decision, decision, decision)
    )

    return updated_requirement is not None


def reset_failed_salary_reassessment(requirement_id):
    # Restore a failed reassessment to the Admin's pending review queue.
    query = """
        UPDATE household_requirements
        SET salary_review_decision = 'PENDING'
        WHERE requirement_id = %s
          AND status = 'SALARY_REVIEW_REQUESTED'
          AND salary_review_decision = 'REASSESSMENT_REQUESTED'
    """

    # Execute the update using a parameterized requirement ID.
    execute_query(query, (requirement_id,))

    # Confirm that the request is now pending and can be retried.
    pending_request = fetch_one(
        """
        SELECT requirement_id
        FROM household_requirements
        WHERE requirement_id = %s
          AND status = 'SALARY_REVIEW_REQUESTED'
          AND salary_review_decision = 'PENDING'
        """,
        (requirement_id,),
    )

    return pending_request is not None


    # The first operation inserts the requirement.
    # Its generated ID will be used by the service layer
    # in a follow-up step, so we cannot yet build all
    # dependent operations here without knowing that ID.
    #
    # This function will be completed in the next step
    # after we establish how to retrieve that ID within
    # the same transaction.



def submit_requirement_for_matching(requirement_id, customer_id):
    """
    Submit a customer's salary-estimated requirement for Admin matching.
    The update is restricted to the owning customer and an eligible status.
    """
    query = """
        UPDATE household_requirements
        SET status = 'SUBMITTED'
        WHERE requirement_id = %s
          AND customer_id = %s
          AND status = 'SALARY_ESTIMATED'
          AND estimated_monthly_salary IS NOT NULL
    """
    execute_query(query, (requirement_id, customer_id))

    submitted = fetch_one(
        """
        SELECT requirement_id
        FROM household_requirements
        WHERE requirement_id = %s
          AND customer_id = %s
          AND status = 'SUBMITTED'
          AND estimated_monthly_salary IS NOT NULL
        """,
        (requirement_id, customer_id),
    )
    return submitted is not None

def get_submitted_requirements_for_admin():
    """Return household requirements awaiting Admin review."""
    query = """
        SELECT
            requirement_id,
            customer_id,
            location_address,
            city,
            state,
            pincode,
            experience_requirement,
            status,
            estimated_monthly_salary,
            created_at
        FROM household_requirements
        WHERE status IN ('SUBMITTED', 'UNDER_REVIEW')
        ORDER BY created_at ASC
    """

    return fetch_all(query, ())
"""This function:
- Returns requirements from all customers for Admin review.
- Includes only SUBMITTED and UNDER_REVIEW requirements.
- Leaves existing records and customer-specific queries unchanged."""