from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db, MovieModel


router = APIRouter()

@router.get("/movies/")
async def get_movies(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db),
):
    # local imports (can't change top-of-file imports)
    from sqlalchemy import select, func

    # total_items (async)
    total_items = await db.scalar(select(func.count()).select_from(MovieModel))
    if not total_items:
        raise HTTPException(status_code=404, detail="No movies found.")

    total_pages = (total_items + per_page - 1) // per_page
    offset = (page - 1) * per_page

    result = await db.execute(
        select(MovieModel).order_by(MovieModel.id.asc()).offset(offset).limit(per_page)
    )
    movies = result.scalars().all()

    if not movies:
        raise HTTPException(status_code=404, detail="No movies found.")

    prev_page = f"/theater/movies/?page={page - 1}&per_page={per_page}" if page > 1 else None
    next_page = f"/theater/movies/?page={page + 1}&per_page={per_page}" if page < total_pages else None

    return {
        "movies": [
            {
                "id": m.id,
                "name": m.name,
                "date": m.date,
                "score": m.score,
                "genre": m.genre,
                "overview": m.overview,
                "crew": m.crew,
                "orig_title": m.orig_title,
                "status": m.status,
                "orig_lang": m.orig_lang,
                "budget": m.budget,
                "revenue": m.revenue,
                "country": m.country,
            }
            for m in movies
        ],
        "prev_page": prev_page,
        "next_page": next_page,
        "total_pages": total_pages,
        "total_items": total_items,
    }


@router.get("/movies/{movie_id}/")
async def get_movie_by_id(movie_id: int, db: Session = Depends(get_db)):
    movie = await db.get(MovieModel, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie with the given ID was not found.")

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
