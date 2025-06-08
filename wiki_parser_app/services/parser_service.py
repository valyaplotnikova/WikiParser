import asyncio
from urllib.parse import unquote
from uuid import UUID

import aiohttp
from typing import List, Set, Optional
from bs4 import BeautifulSoup
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from wiki_parser_app.models.articles import Article
from wiki_parser_app.repositories.article_repo import ArticleRepository


class WikipediaParser:
    def __init__(self, session: AsyncSession, max_depth: int = 5, max_concurrent: int = 10):
        self.session = session
        self.repo = ArticleRepository(session)
        self.max_depth = max_depth
        self.max_concurrent = max_concurrent
        self.base_url = "https://ru.wikipedia.org"
        self.visited_urls: Set[str] = set()
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.timeout = aiohttp.ClientTimeout(total=30)

    async def parse_article(self, url: str, depth: int = 0, parent_id: Optional[UUID] = None) -> List[Article]:
        if depth > self.max_depth:
            return []

        clean_url = self._normalize_url(url)
        full_url = f"{self.base_url}/wiki/{clean_url}"

        if full_url in self.visited_urls:
            return []
        self.visited_urls.add(full_url)

        try:
            async with self.semaphore:
                article_data = await self._fetch_article(full_url)
                if not article_data:
                    return []

                article = await self.repo.save(
                    url=clean_url,
                    title=article_data['title'],
                    content=article_data['content'],
                    parent_id=parent_id
                )

                if not article:
                    return []

                results = [article]

                if depth < self.max_depth:
                    child_links = self._extract_valid_links(article_data['soup'])
                    tasks = [
                        self.parse_article(
                            url=link,
                            depth=depth + 1,
                            parent_id=article.id
                        )
                        for link in child_links[:self.max_concurrent]
                    ]

                    child_results = await asyncio.gather(*tasks, return_exceptions=True)
                    for res in child_results:
                        if isinstance(res, list):
                            results.extend(res)

                return results

        except Exception as e:
            logger.error(f"Error parsing {url}: {str(e)}")
            return []

    async def _fetch_article(self, url: str) -> Optional[dict]:
        """Получение и разбор страницы"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
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
