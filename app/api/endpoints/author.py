from fastapi import APIRouter,Depends,HTTPException,status
from typing import List
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app import model
from app.schemas import category
from app.schemas.author import Author,AuthorUpdate,AuthorCreate

router = APIRouter()

@router.get('/',response_model=List[Author])
def list_authors(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    author = db.query(model.Author).offset(skip).limit(limit).all()
    return author

@router.get("/{author_id}",response_model=Author)
def get_author(
    author_id: int,
    db:Session = Depends(get_db)
):
    author = db.query(model.Author).filter(model.Author.id == author_id).first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found"
        )
    return author

@router.post("/",response_model=Author,status_code=status.HTTP_201_CREATED)
def create_author(
    author_in:AuthorCreate,
    db:Session = Depends(get_db)
):
    existing = db.query(model.Author).filter(model.Author.name == author_in.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Author with name already exists"
        )
    author = model.Author(name=author_in.name,bio=author_in.bio)
    db.add(author)
    db.commit()
    db.refresh(author)
    return author

@router.put("/{author_id}",response_model=Author)
def update_author(
    author_id: int,
    author_in:AuthorUpdate,
    db:Session = Depends(get_db)
):
    author = db.query(model.Author).filter(model.Author.id == author_id).first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found"
        )
    if author_in.name is not None and author_in.name != author.name:
        existing = db.query(model.Author).filter(model.Author.name == author_in.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Author with name already exists"
            )
        author.name = author_in.name
    if author_in.bio is not None:
        author.bio = author_in.bio
    db.add(author)
    db.commit()
    db.refresh(author)
    return author

@router.delete("/{author_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_author(
    author_id: int,
    db:Session = Depends(get_db)
):
    author = db.query(model.Author).filter(model.Author.id == author_id).first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found"
        )
    db.delete(author)
    db.commit()
    return None