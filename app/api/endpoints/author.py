from fastapi import APIRouter

router = APIRouter()

@router.get('/')
def list_authors():
    return {"message" : "List authors"}