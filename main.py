from fastapi import FastAPI,Depends,HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal,engine
import models
from sqlalchemy import text


models.Base.metadata.create_all(bind=engine)

app= FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/')
def health(db:Session=Depends(get_db)):
    try:
        db.execute(text("SELECT 1;"))
        return { "Status":"Ok" ,"db":"up"}
    except Exception:
        raise HTTPException(status_code=503,detail={"Status":"error","db":"down"})
@app.post("/user/")
def create_user(name:str,email:str,password:str,role:str,db:Session=Depends(get_db)):
    db_user=db.query(models.User).filter(models.User.email==email).first()
    if db_user:
        raise HTTPException(status_code=400,detail="Email already exists")
    new_user=models.User(name=name,email=email,hashed_password=password,role=role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
@app.get("/users/")
def get_users(db:Session=Depends(get_db)):
    return db.query(models.User).all()
@app.delete("/users/{id}")
def delete_user(id:int,db:Session=Depends(get_db)):
    user=db.query(models.User).filter(models.User.id==id).first()
    if not user:
        raise HTTPException(status_code=404 , detail="User not Found")
    db.delete(user)
    db.commit()
    return {"Deleted":user}