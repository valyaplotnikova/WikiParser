from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from wiki_parser_app.core.config import api_key
from wiki_parser_app.dependencies.repository_dep import get_session_with_commit
from wiki_parser_app.repositories.article_repo import ArticleRepository
from wiki_parser_app.repositories.summary_repo import SummaryRepository
from wiki_parser_app.schemas.article import ParseRequestSchema, ArticleResponseSchema
from wiki_parser_app.services.article_service import ArticleService
from wiki_parser_app.services.llm_service import SummaryService
from wiki_parser_app.services.parser_service import WikipediaParser

router = APIRouter()


@router.post('/parse', response_model=ArticleResponseSchema)
async def parse_article(
        request: ParseRequestSchema,
        session: AsyncSession = Depends(get_session_with_commit)
):
    try:
        article_repo = ArticleRepository(session)
        summary_repo = SummaryRepository(session)
        parser = WikipediaParser(session)
        llm_service = SummaryService(api_key=api_key)

        service = ArticleService(article_repo, summary_repo, parser, llm_service)
        article = await service.parse_and_save_article(request.url)

        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        return {
            "id": article.id,
            "url": article.url,
            "title": article.title,
        }

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
