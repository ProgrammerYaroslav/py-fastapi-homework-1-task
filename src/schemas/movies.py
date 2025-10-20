from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class MovieDetailResponseSchema(BaseModel):
    """
    Схема для детальної інформації про один фільм.
    """
    id: int
    name: str
    date: date
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
        """Вказує Pydantic читати дані з атрибутів моделі SQLAlchemy."""
        from_attributes = True


class MovieListResponseSchema(BaseModel):
    """
    Схема для відповіді зі списком фільмів та інформацією про пагінацію.
    """
    movies: List[MovieDetailResponseSchema]
    prev_page: Optional[str] = Field(None, description="Посилання на попередню сторінку")
    next_page: Optional[str] = Field(None, description="Посилання на наступну сторінку")
    total_pages: int = Field(..., description="Загальна кількість сторінок")
    total_items: int = Field(..., description="Загальна кількість фільмів")
