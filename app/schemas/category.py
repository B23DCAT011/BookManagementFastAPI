from pydantic import  BaseModel

class CategoryBase(BaseModel):
    name:str
    description:str | None = None

class CategoryCreate(CategoryBase):
    """Schema for create Category"""
    pass
class CategoryUpdate(BaseModel):
    """Schema for update Category"""
    name: str |None = None
    description:str| None = None
class CategoryInDBBase(CategoryBase):
    id:int

    class Config:
        orm_mode = True #Pydantic read from SQLAlchemy model

class Category(CategoryInDBBase):
    """Schema return for client"""
    pass