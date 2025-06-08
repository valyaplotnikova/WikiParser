import asyncio

from urllib.parse import unquote
from uuid import UUID

import aiohttp
from typing import List, Optional
from bs4 import BeautifulSoup
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from wiki_parser_app.models.articles import Article


class WikipediaParser:
    def __init__(self, session: AsyncSession, max_depth: int = 5):
        self.session = session
        self.max_depth = max_depth
        self.visited_urls = set()
        self.semaphore = asyncio.Semaphore(10)

    async def parse_article(self, url: str, depth: int = 0, parent_id: Optional[UUID] = None) -> List[Article]:
        if depth > self.max_depth:
            return []

        clean_url = self._normalize_url(url)
        full_url = f"https://ru.wikipedia.org/wiki/{clean_url}"

        if full_url in self.visited_urls:
            return []
        self.visited_urls.add(full_url)

        try:
            async with self.semaphore:
                article_data = await self._fetch_article(full_url)
                if not article_data:
                    return []

                article = Article(
                    title=article_data['title'],
                    url=clean_url,
                    content=article_data['content'],
                    level=depth,
                    parent_id=parent_id
                )

                self.session.add(article)
                await self.session.flush()

                if depth < self.max_depth:
                    child_links = self._extract_valid_links(article_data['soup'])
                    tasks = [
                        self.parse_article(link, depth + 1, article.id)
                        for link in child_links[:10]
                    ]
                    await asyncio.gather(*tasks)

                return [article]

        except Exception as e:
            logger.error(f"Error parsing {url}: {e}")
            return []

    async def _fetch_article(self, url: str) -> Optional[dict]:
        """Получение и разбор страницы"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.warning(f"HTTP {response.status} for {url}")
                        return None
                    html = await response.text()

            soup = BeautifulSoup(html, 'html.parser')
            title = soup.find("h1").text if soup.find("h1") else "No Title"
            content_div = soup.find("div", {"id": "bodyContent"})
            content = content_div.get_text(strip=True)[:100000] if content_div else "No Content"

            return {
                'url': self._normalize_url(url),
                'title': title,
                'content': content,
                'soup': soup
            }
        except Exception as e:
            logger.error(f"Fetch error: {str(e)}")
            return None

    async def _save_article(self, **kwargs) -> Optional[Article]:
        """Сохранение статьи в БД"""
        try:
            return await self.repo.save(**kwargs)
        except Exception as e:
            logger.error(f"Save error: {str(e)}")
            return None

    def _extract_valid_links(self, soup: BeautifulSoup) -> List[str]:
        """Извлечение только валидных wiki-ссылок"""
        links = set()
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if href.startswith("/wiki/") and not any(x in href for x in [":", "#", "//"]):
                links.add(href.split('/wiki/')[-1])
        return list(links)[:10]

    def _normalize_url(self, url: str) -> str:
        """Нормализация URL с декодированием"""
        url = url.split('/wiki/')[-1].split('#')[0].split('?')[0]
        return unquote(url)
