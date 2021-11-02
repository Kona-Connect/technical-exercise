import time
from typing import Any, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlmodel import Field, Session, SQLModel, create_engine, select


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None

      
engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)
# Create an instance of the API class
app = FastAPI()
security = HTTPBasic(auto_error=False)

# NOTE: This authentication implementation is not complete nor robust. It
# is only meant to be used as an example.
@app.get("/")
async def root(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username if credentials else "World"
    return {"message": "Hello {}".format(username)}

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
