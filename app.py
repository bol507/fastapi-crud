from typing import List
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
import fastapi.security as OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import jwt as _jwt
import schemas as _schemas
import services as _services
import database as _database

app = FastAPI()

@app.post("/api/v1/users")
async def register_user(user: _schemas.UserRequest, db:Session = Depends(_database.get_db)):
  db_user = await _services.getUserByEmail(email=user.email, db=db)
  if db_user:
    raise HTTPException(status_code=400, detail="User already exists")
  
  db_user = await _services.createUser(user=user, db=db)
  resp = await _services.create_token(user=db_user)
  return resp

@app.get("/api/v1/users")
async def get_users( db: Session = Depends(_database.get_db)):
    return await _services.getAllUsers(db=db)

@app.post("/api/v1/login")
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(_database.get_db)
):
    db_user = await _services.login(email=form_data.username, 
                                    password=form_data.password, 
                                    db=db)
    
    if not db_user:
        raise HTTPException(status_code=400, detail="Wrong login credentials")
  
    return await _services.create_token(db_user)

@app.get("/api/v1/users/current-user",response_model=_schemas.UserResponse)
async def current_user(user: _schemas.UserResponse = Depends(_services.current_user)):
    return user 

@app.post("/api/v1/posts", response_model = _schemas.PostResponse)
async def create_post(post_request: _schemas.PostRequest, user: _schemas.UserRequest = Depends(_services.current_user), db: Session = Depends(_database.get_db)):
    return await _services.create_post(user = user, db = db, post= post_request)

@app.get("/api/v1/posts/users", response_model=List[_schemas.PostResponse])
async def get_posts_by_user(user: _schemas.UserRequest = Depends(_services.current_user),  db: Session = Depends(_database.get_db)):
    return await _services.get_posts_by_user(user=user, db=db)