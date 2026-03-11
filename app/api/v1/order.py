from fastapi import APIRouter,Depends
from app.models.order import Order
from app.schemas.order import OrderResponse,OrderCreateRequest
from app.services import order_service
from app.services.auth_service import get_current_user
from app.api.deps import get_db
router = APIRouter(prefix='/api/1/orders',tags=['orders'])

@router.post("/create",response_model=OrderResponse)
def create_order(payload:OrderCreateRequest,current_user=Depends(get_current_user), db = Depends(get_db) ):
    order=order_service.create_order(db,current_user.id,payload.p_name,payload.quantity)
    return {
        "msg":'success',
        "code" :'200',
        "data":order
    }
