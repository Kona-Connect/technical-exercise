from __future__ import print_function

import time
from typing import Any

from fastapi import FastAPI, HTTPException

from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=int(time.time()), primary_key=True)
    name: str
    secret_name: str
    age: Optional[str] = None


engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)
# Create an instance of the API class
app = FastAPI()


@app.get("/")
async def root():  # some information (about the user) is missing here
    # TODO include the user's name if they are logged in
    with Session(engine) as session:
        logged_in = False

        # Either it must be checked here whether the user is logged in or the possibility of logging in must be given
        # and the input data must be compared with those from the database.
        # I would have to read something about authentication with FastAPI before implementing this assignment,
        # but I would take this as a baseline: https://fastapi.tiangolo.com/tutorial/security/get-current-user/

        user = User(name="Dummy", secret_name="dummyuser")  # TODO replace with real user name
        if logged_in:
            return {"message": "Hello {}".format(user.name)}
        return {"message": "Hello {}".format("World")}


@app.post("/user")
async def create_new_user(*, user: User):
    with Session(engine) as session:
        # check if user ID exists
        #   Alternatively, the ID could be increased by (e. g.) 1 each, but since the default value time.time()
        #   is of the float data type, but the default of the data model is int, this would have a big negative impact
        #   on performance when adding many users at once.
        #   Or one has to use float as data type or another library than "time"
        statement = select(User).where(User.id == user.id)
        user_count = len(session.exec(statement).all())
        if user_count > 0:
            return {"message": "User {} already exists".format(user.id)}

        # add user to DB
        session.add(user)
        session.commit()

        return {"message": "User {} created".format(user.id)}  # was wrong indented


@app.get("/user/{id}")
async def get_user(id: int):
    with Session(engine) as session:
        statement = select(User).where(User.id == id)  # was User.name
        user = session.exec(statement).first()
        if user is not None:
            return {"user": user}
        else:
            raise HTTPException(status_code=404, detail="User {} could not be found".format(id))


@app.get("/api/webhooks")
async def handle_hook(*, event: Any):
    id = event.payload.conversation.id
    return {"message": "Hello World"}
