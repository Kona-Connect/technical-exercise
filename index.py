from __future__ import print_function

import time

from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException

from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select


def get_current_timestamp():
    current_timestamp: float = time.time() #e.g 1634600421.005548
    return int(str(current_timestamp).split(".")[0])

class User(SQLModel, table=True):
    # TODO change the default value to the timestamp that the user is created !DONE
    # default_factory method should be used as a callable would be required to get the current_timestamp
    id: Optional[int] = Field(
        primary_key=True, default_factory=get_current_timestamp)
    name: str
    secret_name: str
    age: Optional[str] = None


DB_URL="sqlite:///database.db"
engine = create_engine(DB_URL)
SQLModel.metadata.create_all(engine)
# Create an instance of the API class
app = FastAPI()


@app.get("/")
async def root(request: Request):
    # TODO include the user's name if they are logged in !DONE
    try:
        return {"message": "Hello {}".format(request.user.name)}
    except Exception:
        return {"message": "Hello {}".format("World")}


@app.post("/user")
async def create_new_user(*, user: User):
    # deleting user provided id to use default id
    user.id = None

    # keep session alive for refresh after commit
    with Session(engine, expire_on_commit=False) as session:
        session.add(user)
        session.commit()
    # TODO return the User ID !DONE
    return {"message": "User created", "user_id": user.id}


@app.get("/user/{id}")
async def get_user(id: int):
    with Session(engine) as session:
        # TODO return the user based on the ID (and an error if not) !DONE
        # changed to query to look for the user.id instead of user.name
        statement = select(User).where(User.id == id)
        user = session.exec(statement).first()
        if user:
            return {"user": user}
        return HTTPException(status_code=404, error="user_not_found")


@app.get("/api/webhooks")
async def handle_hook(*, event: Any):
    id = event.payload.conversation.id
    return {"message": "Hello World"}
