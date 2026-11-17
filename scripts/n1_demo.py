from sqlalchemy import event , create_engine,select
from sqlalchemy.orm import selectinload,sessionmaker

from dotenv import load_dotenv
import os

from models import Ticket,User

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"),echo=True)
SessionLocal = sessionmaker(bind=engine)

query_count = 0 

@event.listens_for(engine,"before_cursor_execute")
def count_queries(*args,**kwargs):
    global query_count
    query_count +=1

def list_ticket_naive(session):
    tickets = session.execute(select(Ticket)).scalars().all()
    result = []
    for t in tickets:
        result.append({"id":t.id,"title":t.title,"owner":t.owner.name})
    return result

def list_ticket_fixed(session):
    tickets = session.execute(
        select(Ticket).options(selectinload(Ticket.owner))
    ).scalars().all()
    return [{"id":t.id,"title":t.title,"owner":t.owner.name}for t in tickets]

if __name__=="__main__":
    session = SessionLocal()
    try:

        query_count =0
        list_ticket_naive(session)
        print(f"\nNAIVE Query Count: {query_count}")

        query_count=0
        list_ticket_fixed(session)
        print(f"\nFIXED Query Count: {query_count}")
    finally:
        session.close()