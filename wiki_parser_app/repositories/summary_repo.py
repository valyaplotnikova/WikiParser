from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from wiki_parser_app.models.articles import Summary


class SummaryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, article_id: int, content: str) -> Optional[str]:
        try:
            summary = Summary(article_id=article_id, content=content)
            self.session.add(summary)
            await self.session.flush()
            return content
        except Exception as e:
            await self.session.rollback()
            raise e
