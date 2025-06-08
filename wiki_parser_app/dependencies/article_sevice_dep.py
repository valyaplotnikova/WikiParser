from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from wiki_parser_app.core.config import api_key
from wiki_parser_app.dependencies.repository_dep import get_session_with_commit
from wiki_parser_app.repositories.article_repo import ArticleRepository
from wiki_parser_app.repositories.summary_repo import SummaryRepository
from wiki_parser_app.services.article_service import ArticleService
from wiki_parser_app.services.llm_service import SummaryService
from wiki_parser_app.services.parser_service import WikipediaParser


def get_article_repo(session: AsyncSession = Depends(get_session_with_commit)) -> ArticleRepository:
    return ArticleRepository(session)


def get_summary_repo(session: AsyncSession = Depends(get_session_with_commit)) -> SummaryRepository:
    return SummaryRepository(session)


def get_parser(session: AsyncSession = Depends(get_session_with_commit)) -> WikipediaParser:
    return WikipediaParser(session)


def get_llm_service() -> SummaryService:
    return SummaryService(api_key=api_key)


def get_article_service(
    article_repo: ArticleRepository = Depends(get_article_repo),
    summary_repo: SummaryRepository = Depends(get_summary_repo),
    parser: WikipediaParser = Depends(get_parser),
    llm_service: SummaryService = Depends(get_llm_service)
) -> ArticleService:
    return ArticleService(article_repo, summary_repo, parser, llm_service)
