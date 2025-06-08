from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from wiki_parser_app.dependencies.repository_dep import get_session_without_commit
from wiki_parser_app.repositories.article_repo import ArticleRepository
from wiki_parser_app.repositories.summary_repo import SummaryRepository
from wiki_parser_app.schemas.article import ArticleSummarySchema

router = APIRouter()


@router.get('/summary', response_model=ArticleSummarySchema)
async def get_summary(url: str,
                      session: AsyncSession = Depends(get_session_without_commit)):
    repo = ArticleRepository(session)
    article = await repo.get_by_url(url)
    if not article:
        return {"error": "Статья не найдена"}
    summary = SummaryRepository(session).create(article.id, article.content)
    return summary
