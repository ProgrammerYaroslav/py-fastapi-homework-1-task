from math import ceil
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import MovieModel
from database.session import get_db
from schemas.movies import MovieDetailResponseSchema, MovieListResponseSchema

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get(
    "/",
    response_model=MovieListResponseSchema,
    summary="Get a Paginated List of Movies"
)
async def get_movies_list(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="The page number to fetch."),
    per_page: int = Query(
        10, ge=1, le=20, description="Number of movies to fetch per page."
    ),
):
    """
    Отримує список фільмів з пагінацією.
    """
    # Підрахунок загальної кількості фільмів
    count_query = select(func.count(MovieModel.id))
    total_items_result = await db.execute(count_query)
    total_items = total_items_result.scalar_one()

    if total_items == 0:
        raise HTTPException(status_code=404, detail="No movies found.")

    # Розрахунок загальної кількості сторінок
    total_pages = ceil(total_items / per_page)

    # Розрахунок зміщення
    offset = (page - 1) * per_page

    # Отримання фільмів для поточної сторінки
    movies_query = select(MovieModel).offset(offset).limit(per_page)
    movies_result = await db.execute(movies_query)
    movies = movies_result.scalars().all()

    # Формування URL для попередньої та наступної сторінок
    # Примітка: FastAPI автоматично об'єднає префікс "/theater" з роутера, 
    # тому тут ми використовуємо відносний шлях.
    base_url = "/theater/movies/"
    prev_page_url = (
        f"{base_url}?page={page - 1}&per_page={per_page}" if page > 1 else None
    )
    next_page_url = (
        f"{base_url}?page={page + 1}&per_page={per_page}" if page < total_pages else None
    )

    return {
        "movies": movies,
        "prev_page": prev_page_url,
        "next_page": next_page_url,
        "total_pages": total_pages,
        "total_items": total_items,
    }


@router.get(
    "/{movie_id}/",
    response_model=MovieDetailResponseSchema,
    summary="Get Movie Details by ID"
)
async def get_movie_details(
    movie_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Отримує детальну інформацію про фільм за його ID.
    """
    query = select(MovieModel).where(MovieModel.id == movie_id)
    result = await db.execute(query)
    movie = result.scalar_one_or_none()

    if movie is None:
        raise HTTPException(
            status_code=404, detail="Movie with the given ID was not found."
        )

    return movie
