from app.database import fetch_one


def get_admin_dashboard_stats():
    stats = {}

    # Total Customers
    stats["total_customers"] = fetch_one(
        "SELECT COUNT(*) AS total FROM users WHERE role = 'CUSTOMER'"
    )["total"]

    # Total Maids
    stats["total_maids"] = fetch_one(
        "SELECT COUNT(*) AS total FROM users WHERE role = 'MAID'"
    )["total"]

    # Pending Maid Verifications
    stats["pending_verifications"] = fetch_one(
        "SELECT COUNT(*) AS total FROM maid_verifications WHERE status = 'PENDING'"
    )["total"]

    # Pending Household Requirements
    stats["pending_requirements"] = fetch_one(
        """
        SELECT COUNT(*) AS total
        FROM household_requirements
        WHERE status IN ('SUBMITTED', 'UNDER_REVIEW', 'SALARY_REVIEW_REQUESTED')
        """
    )["total"]

    # Active Employments
    stats["active_employments"] = fetch_one(
        "SELECT COUNT(*) AS total FROM employments WHERE status = 'ACTIVE'"
    )["total"]

    # Pending Assignments
    stats["pending_assignments"] = fetch_one(
        """
        SELECT COUNT(*) AS total
        FROM maid_assignments
        WHERE status = 'PENDING_MAID_RESPONSE'
        """
    )["total"]

    return stats