"""Read-only monthly attendance reporting queries."""

from datetime import date

from app.database import fetch_all


def get_monthly_attendance_report(year, month):
    """
    Return daily attendance counts for one calendar month.

    Only attendance records that actually exist are counted.
    Missing dates are not treated as absences.
    """

    try:
        year = int(year)
        month = int(month)
        month_start = date(year, month, 1)
    except (TypeError, ValueError):
        raise ValueError("A valid year and month are required.")

    if month == 12:
        next_month_start = date(year + 1, 1, 1)
    else:
        next_month_start = date(year, month + 1, 1)

    query = """
        SELECT
            a.attendance_date,
            COUNT(*) AS total_records,
            SUM(CASE WHEN a.status = 'CONFIRMED' THEN 1 ELSE 0 END)
                AS confirmed_count,
            SUM(CASE WHEN a.status = 'PENDING' THEN 1 ELSE 0 END)
                AS pending_count,
            SUM(CASE WHEN a.status = 'DISPUTED' THEN 1 ELSE 0 END)
                AS disputed_count,
            SUM(CASE WHEN a.status = 'ADJUSTED' THEN 1 ELSE 0 END)
                AS adjusted_count,
            SUM(CASE WHEN a.status = 'REJECTED' THEN 1 ELSE 0 END)
                AS rejected_count
        FROM attendance a
        WHERE a.attendance_date >= %s
          AND a.attendance_date < %s
        GROUP BY a.attendance_date
        ORDER BY a.attendance_date ASC
    """

    return fetch_all(
        query,
        (month_start, next_month_start)
    )
