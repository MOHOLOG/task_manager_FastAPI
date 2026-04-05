from pydantic import Field, BaseModel, ConfigDict

class CategoryBase(BaseModel):
    name: str = Field(max_length=100)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    name: str | None = Field(default=None, max_length=100)

class CategoryResponse(CategoryBase):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class PaginatedCategoryResponse(BaseModel):
    categories: list[CategoryResponse]
    skip: int
    limit: int
    total: int
    has_more: bool