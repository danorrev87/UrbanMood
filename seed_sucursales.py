"""
Seed script to populate initial sucursales (locations).
Run with: python seed_sucursales.py
"""
from db import SessionLocal
from models import Sucursal

def seed_sucursales():
    db = SessionLocal()
    try:
        if db.query(Sucursal).count() > 0:
            print("Sucursales already seeded. Skipping.")
            return

        sucursales = [
            Sucursal(
                name='Palermo',
                address='Montevideo, Uruguay',
                phone=None
            ),
            Sucursal(
                name='Cordón',
                address='Montevideo, Uruguay',
                phone=None
            ),
        ]

        for s in sucursales:
            db.add(s)

        db.commit()
        print(f"Successfully seeded {len(sucursales)} sucursales!")
        for s in sucursales:
            print(f"   - {s.name}: {s.address}")

    except Exception as e:
        print(f"Error seeding sucursales: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    seed_sucursales()
