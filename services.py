import database as _database
import models as _models
from sqlalchemy.orm import Session
import schemas as _schemas
import email_validator as _email_validator
from fastapi import HTTPException , Depends
import passlib.hash as _hash
import jwt as _jwt
import fastapi.security as _security

_JWT_SECRET = "secret"
oauth2schemas = _security.OAuth2PasswordBearer("/api/v1/login")


async def getUserByEmail(db: Session, email: str):
    return db.query(_models.UserModel).filter(_models.UserModel.email == email).first()

async def getAllUsers(db: Session):
    return db.query(_models.UserModel).all()

async def createUser(user: _schemas.UserRequest, db:Session):

    try:
      isValid = _email_validator.validate_email(user.email)
      email = isValid.email
    except _email_validator.EmailNotValidError:
        raise HTTPException(status_code=400, detail="Invalid email")
    
   
    hashed_password = _hash.bcrypt.hash(user.password)
    

    user_obj = _models.UserModel(
        email=email, 
        name=user.name, 
        phone=user.phone, 
        password_hash= hashed_password
    )

    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)

    return user_obj

async def create_token(user: _models.UserModel):
    user_schema = _schemas.UserResponse.model_validate(user)
    user_dict = user_schema.model_dump()
    del user_dict["created_at"]
    token = _jwt.encode({"user": user_dict}, _JWT_SECRET, algorithms=["HS256"])
    return dict(access_token=token, token_type="bearer")

async def login(email: str, password: str, db: Session):
    db_user = await getUserByEmail(email=email, db=db)

    if not db_user:
        return False
    
    if not db_user.password_verification(password=password):
        return False
    
    return db_user

async def current_user(db: Session = Depends(_database.get_db), 
                        token: str = Depends(oauth2schemas)):
    try:
        payload = _jwt.decode(token, _JWT_SECRET, algorithms=["HS256"])
        
        db_user = db.query(_models.UserModel).get(payload["id"])
    except:
        raise  HTTPException(status_code=401, detail="Wrong credentinals")
        
    #if all ok return DTO
    return _schemas.UserResponse.model_validate(db_user)

async def create_post(user: _schemas.UserResponse, db: Session, post: _schemas.PostRequest):
    post = _models.PostModel(**post.dict(), user_id = user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    #return DTO
    return _schemas.PostResponse.model_validate(post)

async def get_posts_by_user(user: _schemas.UserResponse, db: Session):
    posts = db.query(_models.PostModel).filter_by(user_id=user.id)
    return list(map(_schemas.PostResponse.model_validate(posts), posts))

async def get_post_detail(post_id: int, db: Session):
    db_post = db.query(_models.PostModel).filter(_models.PostModel.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post

async def delete_post(post: _models.PostModel, db: Session):
    db.delete(post)
    db.commit()

async def update_post(post_request: _schemas.PostRequest, post: _models.PostModel, db: Session):
    post.title = post_request.title
    post.description = post_request.description
    post.image = post_request.image

    db.commit()
    db.refresh(post)

    return _schemas.PostResponse.model_validate(post)