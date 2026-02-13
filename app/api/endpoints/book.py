from fastapi import APIRouter,Depends, File,HTTPException,status,Query,UploadFile
from typing import List
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app import model
from app.schemas import category
from app.schemas.book import BookBase,BookCreate,BookUpdate,Book
from pathlib import Path
import uuid

router = APIRouter()

#Folder save cover images
COVER_DIR = Path("app/static/covers/")
COVER_DIR.mkdir(parents=True,exist_ok=True)


@router.get('/')
def list_books(
    db:Session = Depends(get_db),
    skip:int = 0,
    limit:int = 10,
    author_id:int | None = Query(None),
    category_id:int | None = Query(None),
    year :int | None = Query(None),
    keyword:str | None = Query(None)
):
    """Get list of books,include filter:
    - author_id:Filter by author id
    - category_id:Filter by category id
    - year:Filter by published year
    - keyword:Filter by keyword in title or description
    """
    mb = model.Book
    query = db.query(mb)
    if author_id is not None:
        query = query.filter(mb.author_id == author_id)
    if category_id is not None:
        query = query.filter(mb.category_id == category_id)
    if year is not None:
        query = query.filter(mb.published_year == year)
    if keyword is not None:
        keyword_filter = f"%{keyword}%"
        query = query.filter(
            (mb.title.ilike(keyword_filter)) |
            (mb.description.ilike(keyword_filter))
        )
    books = query.offset(skip).limit(limit).all()
    return books

@router.get('/{book_id}',response_model=Book)
def get_book(
    book_id:int,
    db:Session = Depends(get_db)
):
    book = db.query(model.Book).filter(model.Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    return book

@router.post('/',response_model=Book,status_code=status.HTTP_201_CREATED)
def create_book(
    book_in:BookCreate,
    db:Session = Depends(get_db)
):
    author = db.query(model.Author).filter(model.Author.id == book_in.author_id).first()
    category = db.query(model.Category).filter(model.Category.id == book_in.category_id).first()
    if not author:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Author with id {book_in.author_id} does not exist"
        )
    if not category:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Category with id {book_in.category_id} does not exist"
        )
    book = model.Book(
        title=book_in.title,
        description=book_in.description,
        published_year=book_in.published_year,
        author_id=book_in.author_id,
        category_id=book_in.category_id
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

@router.put('/{book_id}',response_model=Book)
def update_book(
    book_id:int,
    book_in:BookUpdate,
    db:Session = Depends(get_db)
):
    """
    allow update author_id and category_id only if the new id exists
    """
    book = db.query(model.Book).filter(model.Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )

    if book_in.author_id is not None and book_in.author_id != book.author_id:
        author = db.query(model.Author).filter(model.Author.id == book_in.author_id).first()
        if not author:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f"Author with id {book_in.author_id} does not exist"
            )
        book.author_id = book_in.author_id
    if book_in.category_id is not None and book_in.category_id != book.category_id:
        category = db.query(model.Category).filter(model.Category.id == book_in.category_id).first()
        if not category:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f"Category with id {book_in.category_id} does not exist"
            )
        book.category_id = book_in.category_id
    
    if book_in.title is not None:
        book.title = book_in.title
    if book_in.description is not None:
        book.description = book_in.description
    if book_in.published_year is not None:
        book.published_year = book_in.published_year
    
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

@router.delete('/{book_id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id:int,
    db:Session = Depends(get_db)
):
    book = db.query(model.Book).filter(model.Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    db.delete(book)
    db.commit()
    return

@router.post("/{book_id}/cover",response_model=Book)
async def upload_cover_image(
    book_id:int,
    file:UploadFile = File(...),
    db:Session = Depends(get_db)
):
    """
    Upload cover image for book
    -Allowed jpg,png
    -Save file to app/static/covers/
    -Update book.cover_image to url static/covers/...
    """
    book = db.query(model.Book).filter(model.Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    #Validate file type
    if file.content_type not in ["image/jpeg","image/png"]:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only jpg and png are allowed."
        )
    #Get file extension
    ext = Path(file.filename).suffix.lower()
    if ext not in [".jpg",".jpeg",".png"]:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Invalid file extension. Only .jpg and .png are allowed."
        )
    #Read file content
    contents = await file.read()

    #Optional,limit file size to 2MB
    max_size = 2*1024*1024
    if len(contents) > max_size:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum limit of 2MB."
        )
    
    #Generate unique filename
    filename = f"book_{book_id}_{uuid.uuid4().hex}{ext}"
    file_path = COVER_DIR / filename

    #Write file to disk
    with open(file_path,"wb") as f:
        f.write(contents)

    #Update book cover_image field
    book.cover_image = f"static/covers/{filename}"

    db.add(book)
    db.commit()
    db.refresh(book)
    return book