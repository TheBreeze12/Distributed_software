from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db_read
from app.services import inventory_service
from app.schemas.inventory import InventoryResponse

router=APIRouter(prefix='/api/v1/inventory',tags=['inventory'])

@router.get("/{p_id}",response_model=InventoryResponse)
def get_inventory(p_id:int,db=Depends(get_db_read)):
    inven= inventory_service.get_inventory_by_pid(db,p_id)
    return {
        'msg':'success',
        'code':200,
        'data':inven
    }
