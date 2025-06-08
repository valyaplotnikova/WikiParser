from typing import Optional
from urllib.parse import unquote

from loguru import logger

from wiki_parser_app.models.articles import Article, Summary
from wiki_parser_app.repositories.article_repo import ArticleRepository
from wiki_parser_app.repositories.summary_repo import SummaryRepository
from wiki_parser_app.services.llm_service import SummaryService
from wiki_parser_app.services.parser_service import WikipediaParser


class ArticleService:
    def __init__(
            self,
            article_repo: ArticleRepository,
            summary_repo: SummaryRepository,
            parser: WikipediaParser,
            llm_service: SummaryService
    ):
        self.article_repo = article_repo
        self.summary_repo = summary_repo
        self.parser = parser
        self.llm_service = llm_service

    async def parse_and_save_article(self, url: str) -> Optional[Article]:
        try:
            articles = await self.parser.parse_article(url)
            root_article = next((a for a in articles if a.url == self._normalize_url(url)), None)

            if root_article and not root_article.summary:
                await self._generate_summary(root_article)

            await self.parser.session.commit()
            return root_article

        except Exception as e:
            await self.parser.session.rollback()
            logger.error(f"Service error: {e}")
            raise

    async def _generate_summary(self, article: Article) -> None:
        if not article.content:
            return

        summary_text = await self.llm_service.generate_summary(article.content)
        if summary_text:
            article.summary = Summary(content=summary_text)


