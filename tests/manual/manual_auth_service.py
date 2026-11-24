from app.services.auth_service import register_user


success, result = register_user(
    full_name="Demo Customer",
    email="demo.customer@maidmate.com",
    phone="9876543210",
    password="TestPassword123",
    role="CUSTOMER"
)

print("Success:", success)
print("Result:", result)