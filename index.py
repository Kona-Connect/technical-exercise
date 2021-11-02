from __future__ import print_function

import time
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException

from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select

class User(SQLModel, table=True):
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
    return {"message": "Hello {}".format("World")}


@app.post("/user")
async def create_new_user(*, user: User):
    with Session(engine) as session:
      if user.id is None:
        user.id = int(time.time())
      session.add(user)
      session.commit()
      return {"message": "User with ID {} created".format(user.id)}
    
@app.get("/user/{id}")
async def get_user(id: int):
  with Session(engine) as session:
     statement = select(User).where(User.id == id)
     user = session.exec(statement).first()
     if user is None:
         raise HTTPException(status_code=404, detail="User not found")
     return {"user": user}

@app.get("/api/webhooks")
async def handle_hook(*, event: Any):
    id = event.payload.conversation.id
    return {"message": "Hello World"}
  








