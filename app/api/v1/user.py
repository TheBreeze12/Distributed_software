from fastapi import APIRouter,Depends
from app.schemas.user import TokenResponse,UserLoginRequest,UserRegisterRequest,UserResponse
from app.api.deps import get_db
from app.services.auth_service import login,register,get_current_user
from app.models.user import User

router = APIRouter(prefix='/api/v1/users',tags=['users'])

@router.post('/login',response_model=TokenResponse)
def login_user(pay_load:UserLoginRequest,db = Depends(get_db)):
    access_token=login(db,pay_load.username,pay_load.password)
    return {
        "access_token":access_token
    }


@router.post("/register",response_model=UserResponse)
def register_user(pay_load:UserRegisterRequest,db = Depends(get_db)):
    user=register(db,pay_load.username,pay_load.password,pay_load.email)
    return user

@router.get("/me",response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
