from faker import Faker
from database import SessionLocal
from models import Ticket,User,Ticket_status,Priorities
import random

fake = Faker()

def seed_tickets(count:int=10_000):
    db = SessionLocal()

    try:
        user_ids = [u.id for u in db.query(User.id).all()]
        if not user_ids:
            print("No users found : Seed users first")
            return

        tickets=[]
        for _ in range(count):
            ticket = Ticket(
                title = fake.sentence(nb_words=6).rstrip("."),
                description = fake.paragraph(nb_sentences=3),
                status = random.choice(list(Ticket_status)),
                priority = random.choice(list(Priorities)),
                owner_id = random.choice(user_ids)
            )
            tickets.append(ticket)

        db.add_all(tickets)
        db.commit()
        print(f"Seeded {count} tickets.")
    except Exception as e:
        db.rollback()
        print(f"Failed: {e}")
        raise
    finally:
        db.close()

if __name__=="__main__":
    seed_tickets(10_000)