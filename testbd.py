import bcrypt

def test_password():
    password = "dental2024"
    hashed = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN.B3UHGGQsY.PNPvqKO."
    
    # Verificar la contraseña
    salt = hashed[:29].encode('utf-8')
    calculated = bcrypt.hashpw(password.encode('utf-8'), salt)
    stored = hashed.encode('utf-8')
    
    print(f"Password: {password}")
    print(f"Salt: {salt}")
    print(f"Calculated: {calculated}")
    print(f"Stored: {stored}")
    print(f"Match: {calculated == stored}")

test_password()