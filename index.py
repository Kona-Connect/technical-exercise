from __future__ import print_function

import time
from typing import Any, Dict, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional
from hashlib import sha256

from sqlmodel import Field, Session, SQLModel, create_engine, select

class User(SQLModel, table=True):
    """Usermodel for the sqlite database

    """
    id: Optional[int] = Field(default=time.time(), primary_key=True) # Uses Unix timestamp
    password: str # password is supposed to be hashed
    name: str
    secret_name: str
    age: Optional[str] = None
      
engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)
# Create an instance of the API class
app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def simple_hash(username:str,password: str):
    """Salts and hashes a password with the username with SHA256

    Args:
        username (str): name of the user
        password (str): raw password of the user

    Returns:
        [str]: hashed password
    """
    salted_hash = username+password
    return str(sha256(salted_hash.encode('utf-8')).hexdigest())

def get_user_info(username: str):
    """Helper function to retrieve a user from the database

    Args:
        username (str): Name of the user 

    Returns:
        [User]: All the user information
    """
    with Session(engine) as session:
        statement = select(User).where(User.name == username)
        user = session.exec(statement).first()
        return user
    
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Posts and validates the login process

    Args:
        form_data (OAuth2PasswordRequestForm, optional): Uses the FastAPI request form . Defaults to Depends().

    Raises:
        HTTPException: 404 Incorrect username or password
        HTTPException: 404 Incorrect username or password

    Returns:
        [dict]: The login access token
    """
    user = get_user_info(form_data.username)
    if user == None:
        raise HTTPException(status_code=404, detail="Incorrect username or password")
    hashed_password = simple_hash(form_data.username, form_data.password)
    if not hashed_password == user.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.name, "token_type": "bearer"}

@app.get("/")
async def root(token: str = Depends(oauth2_scheme)):
    user = get_user_info(token)
    return {"message": "Hello {username}".format(username = user.name)}


@app.post("/user")
async def create_new_user(*, user: User):
    """Creates and registers a new User in the database

    Note:
        Works but FastAPI complains about the instance not being bound to a session.

    Args:
        user (User): A new User Object

    Returns:
        [dict]: Message of the newly created user
    """
    with Session(engine) as session:
        user.password = simple_hash(user.name, user.password) #Hashing password for security
        session.add(user)
        session.commit()
    return {"message": "User {user_id} created".format(user_id = user.id)}
    
@app.get("/user/{id}")
async def get_user(id: int):
    """Gets all the information of an user with the matching ID

    Args:
        id (int): ID of the user

    Raises:
        HTTPException: 404 User ID not found

    Returns:
        [dict]: All the User information
    """
    with Session(engine) as session:
    # TODO return the user based on the ID (and an error if not)
        statement = select(User).where(User.id == id)
        user = session.exec(statement).first()
        if user == None:
            raise HTTPException(status_code=404, detail="User ID not found")
        return {"user": user}

@app.get("/api/webhooks")
async def handle_hook(*, event: Any):
    id = event.payload.conversation.id
    return {"message": "Hello World"}
  








