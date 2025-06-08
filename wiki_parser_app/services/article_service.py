from typing import Optional

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from wiki_parser_app.models.articles import Article, Summary
from wiki_parser_app.repositories.article_repo import ArticleRepository
from wiki_parser_app.repositories.summary_repo import SummaryRepository
from wiki_parser_app.services.llm_service import SummaryService
from wiki_parser_app.services.parser_service import WikipediaParser


class ArticleService:
    def __init__(
            self,
            session: AsyncSession,
            article_repo: ArticleRepository,
            summary_repo: SummaryRepository,
            parser: WikipediaParser,
            llm_service: SummaryService
    ):
        self.session = session
        self.article_repo = article_repo
        self.summary_repo = summary_repo
        self.parser = parser
        self.llm_service = llm_service

    async def parse_and_save_article(self, url: str) -> Optional[Article]:
        try:
            success = await self.parser.parse_article(url)
            if not success:
                logger.warning(f"Parsing completed but no new articles found for {url}")
                return None

            # Get the root article
            normalized_url = self.parser._normalize_url(url)
            article = await self.article_repo.get_by_url(normalized_url)

            if not article:
                logger.error(f"Root article not found after parsing: {url}")
                return None

            # Generate summary
            await self._generate_summary(article)
            await self.session.commit()
            return article

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error in parse_and_save_article: {str(e)}")
            raise

    async def _generate_summary(self, article: Article) -> None:
        try:
            if not article.content:
                logger.warning(f"No content to summarize for article {article.id}")
                return

            summary_text = await self.llm_service.generate_summary(article)

            if not summary_text:
                logger.warning(f"Empty summary generated for article {article.id}")
                return

            summary = Summary(
                article_id=article.id,
                summary=summary_text,
            )
            await self.summary_repo.create(summary.article_id, summary.content)

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise
