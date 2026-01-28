from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import MovieModel, get_db
from schemas.movies import MovieDetailResponseSchema, MovieListResponseSchema

router = APIRouter()


@router.get("/movies/", response_model=MovieListResponseSchema)
async def get_movies(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
) -> dict:
    # Count total items WITHOUT extra imports (flake8-friendly)
    count_stmt = MovieModel.__table__.select().with_only_columns(
        MovieModel.__table__.c.id
    )
    count_result = await db.execute(count_stmt)
    total_items = len(count_result.fetchall())

    if total_items == 0:
        raise HTTPException(status_code=404, detail="No movies found.")

    total_pages = (total_items + per_page - 1) // per_page
    offset = (page - 1) * per_page

    stmt = (
        MovieModel.__table__.select()
        .order_by(MovieModel.__table__.c.id.asc())
        .offset(offset)
        .limit(per_page)
    )
    result = await db.execute(stmt)
    rows = result.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No movies found.")

    if page > 1:
        prev_page = f"/theater/movies/?page={page - 1}&per_page={per_page}"
    else:
        prev_page = None

    if page < total_pages:
        next_page = f"/theater/movies/?page={page + 1}&per_page={per_page}"
    else:
        next_page = None

    movies = []
    for row in rows:
        m = row._mapping  # RowMapping, no extra imports
        movies.append(
            {
                "id": m["id"],
                "name": m["name"],
                "date": m["date"],
                "score": m["score"],
                "genre": m["genre"],
                "overview": m["overview"],
                "crew": m["crew"],
                "orig_title": m["orig_title"],
                "status": m["status"],
                "orig_lang": m["orig_lang"],
                "budget": m["budget"],
                "revenue": m["revenue"],
                "country": m["country"],
            }
        )

    return {
        "movies": movies,
        "prev_page": prev_page,
        "next_page": next_page,
        "total_pages": total_pages,
        "total_items": total_items,
    }


@router.get("/movies/{movie_id}/", response_model=MovieDetailResponseSchema)
async def get_movie_by_id(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    movie = await db.get(MovieModel, movie_id)
    if not movie:
        raise HTTPException(
            status_code=404,
            detail="Movie with the given ID was not found.",
        )

    return {
        "id": movie.id,
        "name": movie.name,
        "date": movie.date,
        "score": movie.score,
        "genre": movie.genre,
        "overview": movie.overview,
        "crew": movie.crew,
        "orig_title": movie.orig_title,
        "status": movie.status,
        "orig_lang": movie.orig_lang,
        "budget": movie.budget,
        "revenue": movie.revenue,
        "country": movie.country,
    }
