from app.auth_utils import hash_password, verify_password


password = "TestPassword123"

password_hash = hash_password(password)

print("Original password:", password)
print("Generated hash:", password_hash)
print("Correct password:", verify_password(password, password_hash))
print("Wrong password:", verify_password("WrongPassword", password_hash))