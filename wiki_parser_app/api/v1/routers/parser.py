from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from wiki_parser_app.dependencies.article_sevice_dep import get_article_service

from wiki_parser_app.schemas.article import ParseRequestSchema, ArticleResponseSchema
from wiki_parser_app.services.article_service import ArticleService


router = APIRouter()


@router.post('/parse', response_model=ArticleResponseSchema)
async def parse_article(
        request: ParseRequestSchema,
        article_service: ArticleService = Depends(get_article_service)
):
    try:
        article = await article_service.parse_and_save_article(request.url)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        return ArticleResponseSchema(
            id=article.id,
            url=article.url,
            title=article.title,
            summary=article.summary.content if article.summary else None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
