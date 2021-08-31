from __future__ import print_function

from datetime import time,datetime

from typing import Any, Dict, Optional

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm 
from fastapi.exceptions import HTTPException
from fastapi import status
from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(SQLModel, table=True):
    # TODO change the default value to the timestamp that the user is created
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: Optional[str] = None
    #the question is not clearly stated and thus ambigous, I could got get what field needed to have the timestamp and the field type
    created_at:Optional[datetime] = None
      
engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)
# Create an instance of the API class
app = FastAPI()

@app.post("/token")
async def token_generate(form_data:OAuth2PasswordRequestForm=Depends()):
    print(form_data)
    return {"access_token":form_data.username,"token_type":"bearer"}


def fake_decode_token(token):
    return User(
        username=token + "fakedecoded", id=1, name="james",age="27"
    )

@app.get("/")
async def root(token: str = Depends(oauth2_scheme)):
    # TODO include the user's name if they are logged in

    user = fake_decode_token(token)
    logged_in_user=user.name
    return {"message": "Hello {logged_in_user}".format(logged_in_user=logged_in_user)}


@app.post("/user")
async def create_new_user(*, user: User):
    with Session(engine) as session:
      session.add(user)
      session.commit()
      user=user.id
    # TODO return the User ID
    return {"User": user}
    
@app.get("/user/{id}")
async def get_user(id: int):
  with Session(engine) as session:
     # TODO return the user based on the ID (and an error if not)
     statement = select(User).where(User.id == id)
     user = session.exec(statement).first()
     if user==None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
     return {"user": user}

@app.get("/api/webhooks")
async def handle_hook(*, event: Any):
    id = event.payload.conversation.id
    return {"message": "Hello World"}
  








