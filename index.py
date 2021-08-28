from __future__ import print_function

import time
from typing import Any, Dict, Optional
import datetime
from sqlalchemy import Column, Integer, DateTime


from fastapi import FastAPI

from typing import Optional

import sqlalchemy as sa

from sqlmodel import Field, Session, SQLModel, create_engine, select
from pydantic import BaseModel

class User(SQLModel, table=True):
    # TODO change the default value to the timestamp that the user is created
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: Optional[str] = None
    created_date: datetime.datetime = Field(sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False))
      
engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)
# Create an instance of the API class
user_1 = User(id=1, name="Peter", secret_name="Peter PArker", age=18)
app = FastAPI()



@app.get("/")
async def root():
    # TODO include the user's name if they are logged in
    return {"message": "Hello {}".format(user_1.name)}




@app.post("/user")
async def create_new_user(id: int, user: User):
    with Session(engine) as session:
      session.add(user)
      session.commit()
    # TODO return the User ID
    return {"message": "User created {}".format(user.id)}
    
@app.get("/user/{id}")
async def get_user(id: int, user: User):
  with Session(engine) as session:
     # TODO return the user based on the ID (and an error if not)
     if id in session:
         return user
     else:
         return {"Error": "Not corresponding"}

@app.get("/api/webhooks")
async def handle_hook(*, event: Any):
    id = event.payload.conversation.id
    return {"message": "Hello World"}
  








