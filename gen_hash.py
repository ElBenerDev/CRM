import bcrypt

def generate_hash(password):
    salt = bcrypt.gensalt(12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

# Generar hashes para cada contraseña
passwords = {
    'dental@clinic.com': 'dental2024',
    'eye@clinic.com': 'eye2024',
    'general@clinic.com': 'general2024'
}

for email, password in passwords.items():
    hashed = generate_hash(password)
    print(f"\n{email}:")
    print(f"Password: {password}")
    print(f"Hash: {hashed}")
    
    # Verificar que el hash funciona
    verified = bcrypt.checkpw(
        password.encode('utf-8'),
        hashed.encode('utf-8')
    )
    print(f"Verificación: {verified}")