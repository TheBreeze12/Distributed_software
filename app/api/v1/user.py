from fastapi import APIRouter,Depends
from app.schemas.user import PasswordRequest,TokenResponse,ChangeUserRequest,UserLoginRequest,UserRegisterRequest,UserResponse
from app.api.deps import get_db
from app.services.auth_service import change_user_password,change_user_info,login,register,get_current_user
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

@router.post("/change",response_model=UserResponse)
def change_user(request:ChangeUserRequest,db=Depends(get_db),current_user=Depends(get_current_user)):
    user_data=request.dict(exclude_unset=True)
    user=change_user_info(current_user.id,db,**user_data)
    return user

@router.post("/password",response_model=UserResponse)
def change_password(request:PasswordRequest,db=Depends(get_db),current_user=Depends(get_current_user)):
    result=change_user_password(request.password_old,request.password_new,current_user.id,db)
    return result
