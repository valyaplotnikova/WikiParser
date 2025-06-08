from typing import Optional, List
from loguru import logger
from wiki_parser_app.models.articles import Article
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
        """Основной метод для парсинга и сохранения статьи"""
        try:
            articles = await self.parser.parse_article(url)
            root_article = self._find_root_article(articles, url)

            if root_article:

                return root_article
            return None
        except Exception as e:
            logger.error(f"Service error: {str(e)}")
            raise

    def _find_root_article(self, articles: List[Article], original_url: str) -> Optional[Article]:
        """Находит корневую статью по оригинальному URL"""
        clean_url = original_url.split("/wiki/")[-1]
        return next((a for a in articles if a.url.endswith(clean_url)), None)
