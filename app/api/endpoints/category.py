from fastapi import APIRouter,Depends,HTTPException,status
from typing import List
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app import model
from app.schemas.category import Category,CategoryUpdate,CategoryCreate
router = APIRouter()

@router.get('/',response_model=List[Category])
def list_categories(
        skip: int = 0,
        limit: int =100,
        db: Session = Depends(get_db)
):
    categories = db.query(model.Category).offset(skip).limit(limit).all()
    return categories

@router.get("/{category_id}",response_model=Category)
def get_category(
    category_id: int,
    db:Session = Depends(get_db)
):
    category = db.query(model.Category).filter(model.Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return category

@router.post("/",response_model=Category,status_code=status.HTTP_201_CREATED)
def create_category(
    category_in:CategoryCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(model.Category).filter(model.Category.name == category_in.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with name already exists"
        )
    category = model.Category(name = category_in.name,description = category_in.description)
    db.add(category)
    db.commit()
    db.refresh(category)

    return category
@router.put("/{category_id}",response_model=Category)
def update_category(
    category_id: int,
    category_in:CategoryUpdate,
    db:Session = Depends(get_db)
):
    category = db.query(model.Category).filter(model.Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    if category_in.name is not None and category_in.name != category.name:
        existing = db.query(model.Category).filter(model.Category.name == category_in.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Another category with this name"
            )
        category.name = category_in.name
    if category_in.description is not None:
        category.description = category_in.description

    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.delete("/{category_id}",status_code = status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db:Session = Depends(get_db)
):
    category = db.query(model.Category).filter(model.Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    db.delete(category)
    db.commit()

