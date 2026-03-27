from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    source: str

class SearchResponse(BaseModel):
    query: str
    page: int
    per_page: int
    total: int
    results: list[SearchResult]
    searches_today: int
    searches_remaining: int
