
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


    # The first operation inserts the requirement.
    # Its generated ID will be used by the service layer
    # in a follow-up step, so we cannot yet build all
    # dependent operations here without knowing that ID.
    #
    # This function will be completed in the next step
    # after we establish how to retrieve that ID within
    # the same transaction.
