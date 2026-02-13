from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.endpoints import author,category,book

app = FastAPI(
    title="Book Management API",
    description="Simple API to manage books,authors,category and book covers",
    version="1.0.0"
)

app.mount("/static",StaticFiles(directory="app/static"),name="static")

#Include routes
app.include_router(author.router,prefix="/author", tags=["Authors"])
app.include_router(book.router,prefix="/book", tags=["Book"])
app.include_router(category.router,prefix="/category", tags=["Category"])
#Static files for covers image

@app.get("/")
def read_root():
    return {"message" : "Book management API is running"}