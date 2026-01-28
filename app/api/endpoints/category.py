from fastapi import APIRouter

router = APIRouter()

@router.get('/')
def list_categories():
    return {"message" : "List categories"}