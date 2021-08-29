from __future__ import print_function

import time
from typing import Any, Dict, Optional

from fastapi import FastAPI

from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select

class User(SQLModel, table=True):
    # TODO change the default value to the timestamp that the user is created
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: Optional[str] = None
      
engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)
# Create an instance of the API class
app = FastAPI()

@app.get("/")
async def root():
    # TODO include the user's name if they are logged in
        return {"message": "Hello {self.name}".format("World")}


@app.post("/user")
async def create_new_user(*, user: User):
    with Session(engine) as session:
      session.add(user)
      session.commit()
    # TODO return the User ID
    return user.id

    # return {"message": "User created"}
    
@app.get("/user/{id}")
async def get_user(id: int):
  with Session(engine) as session:
     # TODO return the user based on the ID (and an error if not)
    #  I will first create an if statement that check if the id of the 
    # user is equal to the id we have else return an error if it doesnt exist
     statement = select(User).where(User.name == id)
     if statement:
        return {"user": User.name}
     else:
         return "User not found"

@app.get("/api/webhooks")
async def handle_hook(*, event: Any):
    id = event.payload.conversation.id
    return {"message": "Hello World"}
  








