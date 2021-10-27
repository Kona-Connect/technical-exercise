
from __future__ import print_function

import time
from typing import Any, Optional
from fastapi.security import APIKeyCookie
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select
from starlette import status
from starlette.responses import Response
from jose import jwt

def get_current_timestamp():
    return int(time.time())

class User(SQLModel, table=True):
    # The default value is set to the timestamp that the user is created
    id: Optional[int] = Field(default=get_current_timestamp(), primary_key=True)
    name: str
    secret_name: str
    age: Optional[str] = None
      
engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)

# Create an instance of the API class
app = FastAPI()

cookie_sec = APIKeyCookie(name="session", auto_error=False)
secret_key = "someactualsecret"

# This function allows to obtain the current user from the logged session
# I read the following guide: https://github.com/tiangolo/fastapi/issues/754 just to set up some fake login to show the user name
# The login is simulated in the post api (see below)

def get_current_user(session: str = Depends(cookie_sec)):

    if session is None:
        # If there is no session, no user is logged
        return None
    else:
        try:
            # Get the user name from the session
            payload = jwt.decode(session, secret_key, algorithms=['HS256'])
            user = payload["sub"]
            return user
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authentication"
            )


@app.get("/")
async def root(user: str =  Depends(get_current_user)):
    #Include the user's name if they are logged in
    if user is not None:
        return {"message": "Hello {}".format(user)}
    else:
        return {"message": "Hello {}".format("World")}


@app.post("/user")
async def create_new_user(response: Response, * , user: User):
    with Session(engine) as session:
      # check if the user id already exist
      statement = select(User).where(User.id == user.id)
      results = session.exec(statement).all()
      if len(results)>0:
          return {"message": "User with user id {} already exists".format(user.id)}
      else:
        session.add(user)
        session.commit()
        # Simulated a login when creating a user (just to have an example of setting a Cookie with a Token)
        token = jwt.encode({"sub": user.name}, secret_key, algorithm='HS256')
        response.set_cookie("session", token)
        # return the User ID
        return {"message": "User with user id {} has been created".format(user.id)}
    
@app.get("/user/{id}")
async def get_user(id: int):
    with Session(engine) as session:
        # return the user based on the ID (and an error if not)
        statement = select(User).where(User.id == id)
        user = session.exec(statement).first()
        if user is not None:
            return {"user": user}
        else:
            raise HTTPException(status_code=404, detail="User {} could not be found".format(id))

@app.get("/api/webhooks")
async def handle_hook(*, event: Any):
    id = event.payload.conversation.id
    return {"message": "Hello World"}
  








