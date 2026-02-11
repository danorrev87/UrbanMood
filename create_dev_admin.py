#!/usr/bin/env python3
"""Create a dev admin user with known credentials for local development."""

from passlib.hash import bcrypt
from sqlalchemy import select
from db import SessionLocal, engine, Base
from models import User, UserRole

# Create tables if not exist
with engine.begin() as conn:
    Base.metadata.create_all(conn)

def main():
    email = 'admin@dev.local'
    name = 'Dev Admin'
    password = 'admin123'  # Simple password for local dev
    
    with SessionLocal() as db:
        existing = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if existing:
            print(f'Dev admin user already exists: {email}')
            # Update password in case it was changed
            existing.password_hash = bcrypt.hash(password)
            db.commit()
            print('Password updated.')
        else:
            user = User(
                email=email,
                name=name,
                role=UserRole.admin,
                is_active=True,
                password_hash=bcrypt.hash(password)
            )
            db.add(user)
            db.commit()
            print(f'Dev admin created: {email}')
        
        print('\n=== DEV CREDENTIALS ===')
        print(f'Email:    {email}')
        print(f'Password: {password}')
        print('=======================\n')

if __name__ == '__main__':
    main()
