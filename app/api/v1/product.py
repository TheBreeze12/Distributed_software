from fastapi import APIRouter,Depends
from app.services.product_service import get_product_service,get_product_name_service,add_product_service
from app.api.deps import get_db
from app.schemas.product import ProductResponse,ProductAddRequest
router=APIRouter(prefix='/api/v1/products',tags=['products'])

@router.get('/id',response_model=ProductResponse)
def get_product_id(id:int,db=Depends(get_db)):
    data=get_product_service(db,id)
    return {
        "msg":'success',
        "code" :'200',
        "data":data
    }

@router.get('/name',response_model=ProductResponse)
def get_product_id(name:str,db=Depends(get_db)):
    data=get_product_name_service(db,name)
    return {
        "msg":'success',
        "code" :'200',
        "data":data
    }

@router.get("/",response_model=ProductResponse)
def get_all_products(db=Depends(get_db)):
    data=get_product_service(db)
    return {
        "msg":'success',
        "code" :'200',
        "data":data
    }

@router.post("/",response_model=ProductResponse)
def add_one_product(pay_load:ProductAddRequest,db=Depends(get_db)):
    data=add_product_service(db,pay_load.name,pay_load.price)
    return {
        "msg":'success',
        "code" :'200',
        "data":data
    }
