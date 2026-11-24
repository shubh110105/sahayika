import requests

BASE_URL = "http://127.0.0.1:5000"

admin_email = input("Admin email: ")
admin_password = input("Admin password: ")

session = requests.Session()

login_response = session.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": admin_email,
        "password": admin_password
    }
)

print("Login status:", login_response.status_code)
print("Login response:", login_response.text[:1000])

if login_response.status_code == 200:
    salary_response = session.post(
        f"{BASE_URL}/admin/salary-records/generate",
        json={
            "employment_id": 1,
            "salary_month": "2026-10-01"
        }
    )

    print("Salary generation:", salary_response.status_code)
    adjustment_response = session.post(
        f"{BASE_URL}/admin/salary-records/1/adjustments",
        json={
            "attendance_adjustment": 0,
            "leave_adjustment": 0,
            "other_adjustment": 0
        }
    )

    finalize_response = session.post(
        f"{BASE_URL}/admin/salary-records/1/finalize",
        json={}
    )

    print("Finalization status:", finalize_response.status_code)
    print("Finalization response:", finalize_response.json())
    print("Adjustment status:", adjustment_response.status_code)
    print("Adjustment response:", adjustment_response.json())
    locked_adjustment_response = session.post(
        f"{BASE_URL}/admin/salary-records/1/adjustments",
        json={
            "attendance_adjustment": -100,
            "leave_adjustment": 0,
            "other_adjustment": 0
        }
    )

    print(
        "Finalized record adjustment status:",
        locked_adjustment_response.status_code
    )
    print(
        "Finalized record adjustment response:",
        locked_adjustment_response.json()
    )
    print(salary_response.json())