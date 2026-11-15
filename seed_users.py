from faker import Faker
from database import SessionLocal
from models import User

fake = Faker()

def seed_users(count:int=250):
    db =SessionLocal()
    try:
        users=[]
        for _ in range(count):
            user =User(
                name=fake.name(),
                email=fake.email(),
                hashed_password=fake.password()
            )
            users.append(user)

        db.add_all(users)
        db.commit()
        print(f"Seeded {count} users.")
    except Exception as e:
        db.rollback()
        print(f"Failed: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_users(250)