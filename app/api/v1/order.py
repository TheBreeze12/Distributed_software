from fastapi import APIRouter


router = APIRouter(prefix='/api/1/orders',tags=['orders'])

@router.post("/create")
