from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class MovieDetailResponseSchema(BaseModel):
    id: int
    name: str
    date: Optional[date] = None
    score: float
    genre: str
    overview: str
    crew: str
    orig_title: str
    status: str
    orig_lang: str
    budget: int
    revenue: int
    country: str

    class Config:
        orm_mode = True


class MovieListResponseSchema(BaseModel):
    movies: List[MovieDetailResponseSchema]
    prev_page: Optional[str] = None
    next_page: Optional[str] = None
    total_pages: int
    total_items: int
