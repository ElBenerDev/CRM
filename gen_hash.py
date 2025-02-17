from passlib.hash import bcrypt

password = "gen123"
hashed = bcrypt.hash(password)
print(f"Hash para {password}: {hashed}")