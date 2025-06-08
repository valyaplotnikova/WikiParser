from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from wiki_parser_app.core.config import api_key
from wiki_parser_app.dependencies.repository_dep import get_session_with_commit
from wiki_parser_app.repositories.article_repo import ArticleRepository
from wiki_parser_app.repositories.summary_repo import SummaryRepository
from wiki_parser_app.services.article_service import ArticleService
from wiki_parser_app.services.llm_service import SummaryService
from wiki_parser_app.services.parser_service import WikipediaParser


def get_article_service(
        session: AsyncSession = Depends(get_session_with_commit)
) -> ArticleService:
    article_repo = ArticleRepository(session)
    summary_repo = SummaryRepository(session)
    parser = WikipediaParser(session)
    llm_service = SummaryService(api_key=api_key)

    return ArticleService(
        article_repo=article_repo,
        summary_repo=summary_repo,
        parser=parser,
        llm_service=llm_service
    )