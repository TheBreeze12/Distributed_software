from pydantic import BaseModel,Field,EmailStr

class UserLoginRequest(BaseModel):
    username : str
    password : str


class UserRegisterRequest(BaseModel):
    username : str = Field(...,min_length=3,max_length=10)
    password : str = Field(...,min_length=3,max_length=10)
    password_confirm : str = Field(...,min_length=3,max_length=10)
    email : EmailStr = Field(...,title="用户邮箱",examples=["user@example.com"])

class UserResponse(BaseModel):
    id : int
    username : str
    email : EmailStr

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type : str = "bearer"
