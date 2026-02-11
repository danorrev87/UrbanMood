import os
from getpass import getpass
from passlib.hash import bcrypt
from sqlalchemy import select
from db import SessionLocal, engine, Base
from models import User, UserRole

# Create tables if not exist
with engine.begin() as conn:
    Base.metadata.create_all(conn)

def main():
    email = input('Admin email: ').strip().lower()
    name = input('Admin name: ').strip()
    password = getpass('Password (hidden): ')
    with SessionLocal() as db:
        existing = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if existing:
            print('User already exists.')
            return
        user = User(email=email, name=name, role=UserRole.admin, is_active=True, password_hash=bcrypt.hash(password))
        db.add(user)
        db.commit()
        print('Admin created.')

if __name__ == '__main__':
    main()
