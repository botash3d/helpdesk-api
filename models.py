from sqlalchemy import Column,Integer,String,Numeric,DateTime,func,ForeignKey,CheckConstraint
from database import Base
from enum import Enum
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

class Roles(str,Enum):
    user='user'
    admin='admin'

class Ticket_status(str,Enum):
    active='active'
    inactive='inactive'

class Order_status(str,Enum):
    delivered = 'delivered'
    shipped = 'shipped'


class Priorities(str,Enum):
    high='high'
    medium='medium'
    low='low'

class User(Base):
    __tablename__="users"

    id = Column(Integer,primary_key=True,index=True)
    name = Column(String,nullable=False)
    email = Column(String,unique=True,index=True,nullable=False)
    hashed_password = Column(String,nullable=False)
    role = Column(ENUM(Roles,name='user_role'),nullable=False,default=Roles.user)
    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False)

    tickets = relationship("Ticket",back_populates="owner",cascade="all , delete-orphan", passive_deletes=True)

    orders = relationship("Order",back_populates="owner",cascade="all , delete-orphan", passive_deletes=True)

class Ticket(Base):
    __tablename__="tickets"

    id = Column(Integer,primary_key=True,index=True)
    title = Column(String(120),nullable=False)
    description = Column(String,nullable=True)
    status = Column(ENUM(Ticket_status,name="ticket_status"),default=Ticket_status.active,nullable=False)
    priority = Column(ENUM(Priorities,name="ticket_priority"),default=Priorities.medium,nullable=False)
    owner_id = Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    
    owner = relationship("User",back_populates="tickets")

    __table_args__=(CheckConstraint(
        "length(title)>=3",
        name="check_title_min_length"
    ),)

class Order(Base):
    __tablename__="orders"

    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    item = Column(String,nullable=False)
    amount = Column(Numeric(10,2),nullable=False)
    status = Column(ENUM(Order_status,name="order_status"),nullable=False)

    owner = relationship("User",back_populates="orders")