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

@app.get("/api/v1/posts/user", response_model=List[_schemas.PostResponse])
async def get_posts_by_user(user: _schemas.UserRequest = Depends(_services.current_user),  db: Session = Depends(_database.get_db)):
    return await _services.get_posts_by_user(user=user, db=db)

@app.get("/api/v1/posts/all", response_model=List[_schemas.PostResponse])
async def get_posts_by_all(db: Session = Depends(_database.get_db)):
    return await _services.get_posts_by_all(db=db)


@app.get("api/v1/posts/{post_id}/", response_model=_schemas.PostResponse)
async def get_post_detail(post_id: int, db: Session= Depends(_database.get_db)):
    return await _services.get_post_detail(post_id=post_id, db=db)

@app.get("api/v1/users/{user_id}/", response_model=_schemas.UserResponse)
async def get_user_detail(user_id: int, db: Session= Depends(_database.get_db)):
    return await _services.get_user_detail(user_id=user_id, db=db)

@app.delete("api/v1/posts/{post_id}")
async def delete_post(post_id= int, db: Session = Depends(_database.get_db), user: _schemas.UserRequest = Depends(_services.current_user)):
    post = await _services.get_post_detail(post_id=post_id,db=db)
    await _services.delete_post(post=post , db=db)
    return "Post delete sucessful"

@app.put("api/v1/posts/{post_id}", response_model=_schemas.PostResponse)
async def update_post(post_id : int, post_request: _schemas.PostRequest, db: Session = Depends(_database.get_db)):
    db_post = await _services.get_post_detail(post_id=post_id, db=db)
    return await _services.update_post(post_request=post_request, post=db_post, db=db)
