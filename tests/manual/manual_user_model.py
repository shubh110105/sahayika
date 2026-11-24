from app.models.user_model import create_user, get_user_by_email


test_email = "testuser@maidmate.com"

existing_user = get_user_by_email(test_email)

if existing_user:
    print("Test user already exists.")
    print(existing_user)
else:
    user_id = create_user(
        full_name="Test User",
        email=test_email,
        phone="9999999999",
        password="TestPassword123",
        role="CUSTOMER"
    )

    print("Test user created successfully.")
    print("User ID:", user_id)

user = get_user_by_email(test_email)

print("User found:")
print(user)