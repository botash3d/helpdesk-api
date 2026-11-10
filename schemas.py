from pydantic import BaseModel,EmailStr,Field , ConfigDict ,field_validator
from models import Roles,Ticket_status,Order_status,Priorities
from typing import Optional

class UserCreate(BaseModel):
    name:str
    email:EmailStr
    hashed_password:str = Field(min_length=8)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:int
    name:str
    email:EmailStr
    role:Roles

class TicketCreate(BaseModel):
    title:str = Field(min_length=3,max_length=120)
    description:str | None = None
    priority:Priorities
    owner_id:int

class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:int
    title:str
    description:str | None = None
    status:Ticket_status
    priority:Priorities
    owner_id:int

class TicketUpdate(BaseModel):
    title: str =Field(min_length=3,max_length=120)
    description: str | None = None
    status: Ticket_status
    priority: Priorities

class TicketPartialUpdate(BaseModel):
    @field_validator("status","priority")
    @classmethod
    def not_null(cls,v):
        if v is None:
            raise ValueError("cannot be null")
        return v
    model_config = ConfigDict(extra="forbid")
    status: Ticket_status | None = None
    priority: Priorities | None = None
class OrderCreate(BaseModel):
    user_id:int
    item:str
    amount:float
    status:Order_status

class OrderResponse(BaseModel):
    id:int
    user_id:int
    item:str
    amount:float
    status:Order_status