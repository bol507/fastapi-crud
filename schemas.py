import pydantic as _pydantic
import datetime as _datetime

class UserBase(_pydantic.BaseModel):
    email: str
    name: str
    phone: str

class UserRequest(UserBase):
    password:str

    class Config:
        from_attributes = True

class UserResponse(UserBase):
    id: int
    created_at: _datetime.datetime

    class Config:
        from_attributes = True

class PostBase(_pydantic.BaseModel):
    title: str
    description: str
    user_id: int
  
class PostRequest(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    created_at: _datetime.datetime
    user_id: int
    
    class Config:
        from_attributes = True