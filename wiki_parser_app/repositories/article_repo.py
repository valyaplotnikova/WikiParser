from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from sqlalchemy.exc import IntegrityError

from wiki_parser_app.models.articles import Article
from loguru import logger


class ArticleRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def save(
            self,
            url: str,
            title: str,
            content: str,
            parent_id: Optional[UUID] = None
    ) -> Optional[Article]:
        try:
            # Проверяем существование родительской статьи
            if parent_id:
                parent_exists = await self.db_session.execute(
                    select(Article).where(Article.id == parent_id))
                if not parent_exists.scalar():
                    logger.warning(f"Parent article {parent_id} not found")
                return None

            # Проверяем существующую статью
            existing = await self.get_by_url(url)
            if existing:
                return existing

            article = Article(
                url=url,
                title=title,
                content=content,
                parent_id=parent_id
            )

            self.db_session.add(article)
            await self.db_session.flush()
            await self.db_session.refresh(article)
            return article

        except IntegrityError as e:
            await self.db_session.rollback()
            logger.error(f"Integrity error: {str(e)}")
            return await self.get_by_url(url)

        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Unexpected error: {str(e)}")
            return None

    async def get_by_url(self, url: str) -> Optional[Article]:
        result = await self.db_session.execute(
            select(Article).where(Article.url == url))
        return result.scalars().first()
