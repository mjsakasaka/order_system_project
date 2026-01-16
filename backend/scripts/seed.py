"""
Seed script for initializing base data.

Usage (PowerShell):
    $env:ENV="test"; python -m scripts.seed
    $env:ENV="dev";  python -m scripts.seed
"""

from sqlalchemy import select

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.user import User
from app.core.security import hash_password
from app.core.constants import Role

import app.models

# -----------------------------
# Seed data definition
# -----------------------------
DEFAULT_USERS = [
    {
        "username": "admin",
        "password": "admin123",
        "role": Role.ADMIN.value,
    },
    {
        "username": "cs",
        "password": "cs123",
        "role": Role.CS.value,
    },
    {
        "username": "wh",
        "password": "wh123",
        "role": Role.WH.value,
    },
]


# -----------------------------
# Main seed logic
# -----------------------------
def seed_users() -> None:
    """
    Create base users (admin / cs / wh).
    This function is idempotent:
    - Running it multiple times will NOT create duplicates.
    """

    # 1️⃣ Ensure tables exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        for item in DEFAULT_USERS:
            username = item["username"]

            exists = db.execute(
                select(User).where(User.username == username)
            ).scalar_one_or_none()

            if exists:
                print(f"[SKIP] user '{username}' already exists")
                continue

            user = User(
                username=username,
                password_hash=hash_password(item["password"]),
                role=item["role"],
            )
            db.add(user)
            print(f"[CREATE] user '{username}' ({item['role']})")

        db.commit()
        print("✅ Seed users completed successfully")

    finally:
        db.close()


def main() -> None:
    seed_users()


if __name__ == "__main__":
    main()
