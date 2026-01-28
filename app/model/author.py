from sqlalchemy import Column,Integer,String,Text
from sqlalchemy.orm import relationship

from app.db.base import Base

class Author(Base):
    __tablename__ =  "authors"
    id = Column(Integer,primary_key=True,index =True)
    name = Column(String(255),nullable=False,index=True,unique=True)
    bio = Column(Text,nullable=True)

    #Relationship 1-n With Book
    books = relationship("Book" , back_populates="author")

