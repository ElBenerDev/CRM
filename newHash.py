# Puedes ejecutar esto en un script separado para generar los hashes
from app.core.security import get_password_hash

passwords = {
    'dental123': get_password_hash('dental123'),
    'eye123': get_password_hash('eye123'),
    'gen123': get_password_hash('gen123')
}

for k, v in passwords.items():
    print(f"{k}: {v}")