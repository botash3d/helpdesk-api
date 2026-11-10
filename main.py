from fastapi import FastAPI,Depends,HTTPException,status , Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import SessionLocal,engine
from models import User , Ticket , Order , Base
from sqlalchemy import text
from schemas import *


Base.metadata.create_all(bind=engine)

app= FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "up"}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "error", "db": "down"})

@app.exception_handler(StarletteHTTPException)
async def http_exc_handler(request:Request,exc:StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error":{"code":exc.status_code,"message":str(exc.detail)}}
    )

@app.exception_handler(RequestValidationError)
async def validation_exc_handler(request:Request,exc:RequestValidationError):
    first=exc.errors()[0]
    field='.'.join(str(p) for p in first["loc"] if p!= "body")
    return JSONResponse(
        status_code=422,
        content={"error":{"code":422,"message":f"{field}:{first["msg"]}"}}
    )
@app.exception_handler(Exception)
async def unhandled_exc_handler(request:Request,exc:Exception):
    return JSONResponse(
        status_code=500,
        content={"error":{"code":500,"message":"Internal Server Error"}}
    )
    
@app.post("/user/",response_model=UserResponse,status_code=status.HTTP_201_CREATED)
def create_user(user:UserCreate,db:Session=Depends(get_db)):
    db_user=db.query(User).filter(User.email==user.email).first()
    if db_user:
        raise HTTPException(status_code=400,detail="Email already exists")
    new_user=User(name=user.name,email=user.email,hashed_password=user.hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "id":new_user.id,
        "name":new_user.name,
        "email":new_user.email,
        "role":new_user.role
    }
@app.get("/users/",response_model=list[UserResponse])
def get_users(skip:int=0,limit:int=50,db:Session=Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()
@app.delete("/users/{id}")
def delete_user(id:int,db:Session=Depends(get_db)):
    user=db.get(User,id)
    if not user:
        raise HTTPException(status_code=404 , detail="User not Found")
    db.delete(user)
    db.commit()

@app.post("/tickets",response_model=TicketResponse,status_code=status.HTTP_201_CREATED)
def create_ticket(ticket:TicketCreate,db:Session=Depends(get_db)):
    if not db.get(User,ticket.owner_id):
        raise HTTPException(status_code=404,detail="Owner Not Found")
    new_ticket = Ticket(**ticket.model_dump())
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket

@app.get("/tickets",response_model=list[TicketResponse])
def get_all_tickets(skip:int=0,limit:int=50,db:Session=Depends(get_db)):
    return db.query(Ticket).offset(skip).limit(limit).all()

@app.get("/tickets/{id}",response_model=TicketResponse)
def ticket_with_id(id:int,db:Session=Depends(get_db)):
    ticket = db.get(Ticket,id)
    if not ticket:
        raise HTTPException(status_code=404,detail="Ticket Not Found")
    return ticket

@app.put("/tickets/{id}",response_model=TicketResponse,status_code=status.HTTP_200_OK)
def update_full_ticket(id:int , body:TicketUpdate,db:Session=Depends(get_db)):
    t = db.get(Ticket,id)
    if not t:
        raise HTTPException(status_code=404,detail="Ticket Not Found")
    for k , v in body.model_dump().items():
        setattr(t,k,v)
    db.commit()
    db.refresh(t)

    return t
@app.patch("/tickets/{id}",response_model=TicketResponse,status_code=status.HTTP_200_OK)
def update_partial_content(id:int,body:TicketPartialUpdate,db:Session=Depends(get_db)):
    t = db.get(Ticket,id)
    if not t:
        raise HTTPException(status_code=404,detail="Ticket Not Found")
    for k , v in body.model_dump(exclude_unset=True).items():
        setattr(t,k,v)

    db.commit()
    db.refresh(t)

    return t

@app.delete("/tickets/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(id:int,db:Session=Depends(get_db)):
    ticket = db.get(Ticket,id)
    if not ticket:
        raise HTTPException(status_code=404,detail="Ticket Not Found")
    db.delete(ticket)
    db.commit()
