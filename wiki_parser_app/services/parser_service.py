import asyncio
import aiohttp
from html.parser import HTMLParser
import re
from typing import Set, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from wiki_parser_app.models.articles import Article


class WikipediaPageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._level = 0
        self._wrapper_tag = ""
        self._pattern = re.compile(r"^/wiki/(?!.*:).*")
        self._found_links: Set[str] = set()
        self.title = ""
        self.content = ""
        self._in_title = False
        self._in_content = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        attrs_dict = dict(attrs)

        # Detect title
        if tag == "h1" and attrs_dict.get("id") == "firstHeading":
            self._in_title = True

        # Detect content area
        if tag == "div" and attrs_dict.get("id") == "bodyContent":
            self._level = 1
            self._wrapper_tag = tag
            self._in_content = True

        # Collect links
        if self._level > 0 and tag == "a" and "href" in attrs_dict:
            if self._pattern.match(attrs_dict["href"]):
                self._found_links.add(attrs_dict["href"])

        # Skip unwanted elements
        if tag in ["table", "div", "span"] and any(
                attr in attrs_dict.get("class", "")
                for attr in ["hatnote", "thumb", "mw-editsection"]
        ):
            self._skip_element = True

    def handle_data(self, data: str):
        if self._in_title:
            self.title += data
        elif self._in_content and not getattr(self, "_skip_element", False):
            self.content += data + " "

    def handle_endtag(self, tag: str):
        if tag == "h1" and self._in_title:
            self._in_title = False
        if tag == self._wrapper_tag and self._level > 0:
            self._level -= 1
            if self._level == 0:
                self._in_content = False
        if tag == "div" and getattr(self, "_skip_element", False):
            self._skip_element = False

    def get_found_links(self) -> Set[str]:
        return self._found_links


class WikipediaParser:
    def __init__(self, session: AsyncSession, max_depth: int = 5):
        self.session = session
        self.max_depth = max_depth
        self.visited_urls = set()
        self.semaphore = asyncio.Semaphore(10)
        self.base_url = "https://ru.wikipedia.org"

    async def parse_article(self, url: str, depth: int = 0, parent_id: Optional[int] = None) -> bool:
        if depth > self.max_depth:
            return False

        normalized_url = self._normalize_url(url)
        full_url = self._build_full_url(normalized_url)

        if full_url in self.visited_urls:
            return False
        self.visited_urls.add(full_url)

        try:
            async with self.semaphore:
                article_data = await self._fetch_article(full_url)
                if not article_data:
                    return False

                article = Article(
                    title=article_data['title'],
                    url=normalized_url,
                    content=article_data['content'],
                    parsed=True,
                    parent_id=parent_id
                )

                self.session.add(article)
                await self.session.flush()

                if depth < self.max_depth:
                    child_links = article_data['links']
                    tasks = [
                        self.parse_article(link, depth + 1, article.id)
                        for link in child_links[:5]  # Limit child articles
                    ]
                    await asyncio.gather(*tasks)

                return True

        except Exception as e:
            logger.error(f"Error parsing {url}: {str(e)}")
            return False

    async def _fetch_article(self, url: str) -> Optional[dict]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.warning(f"HTTP {response.status} for {url}")
                        return None
                    html = await response.text()

            parser = WikipediaPageParser()
            parser.feed(html)

            return {
                'url': self._normalize_url(url),
                'title': parser.title.strip(),
                'content': parser.content.strip()[:50000],  # Limit content size
                'links': list(parser.get_found_links())
            }

        except Exception as e:
            logger.error(f"Fetch error for {url}: {str(e)}")
            return None

    def _normalize_url(self, url: str) -> str:
        if url.startswith(('http://', 'https://')):
            url = url.split('/wiki/')[-1]
        return url.split('#')[0].split('?')[0].strip()

    def _build_full_url(self, normalized_url: str) -> str:
        return f"{self.base_url}/wiki/{normalized_url}"
