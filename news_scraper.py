from bs4 import BeautifulSoup
from datetime import datetime
import logging
from http_client import safe_request, safe_request_async
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
import asyncio


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class NewsScraperBase(ABC):
    def __init__(self, base_url: str, source_name: str):
        self.base_url = base_url
        self.source_name = source_name
        self.logger = logging.getLogger(__name__)
    
    def scrape_news(self, max_articles: int = 5) -> List[Dict[str, str]]:
        articles = []
        try:
            response = safe_request(self.base_url)
            if not response:
                return articles
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = self._find_news_items(soup, max_articles)
            
            for item in news_items:
                try:
                    article_data = self._extract_article_data(item)
                    if article_data:
                        articles.append(article_data)
                except Exception as e:
                    self.logger.error(f"{self.source_name} 기사 처리 중 오류: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"{self.source_name} 크롤링 중 오류: {e}")
        
        self.logger.info(f"{self.source_name}: {len(articles)} articles found")
        return articles
    
    async def scrape_news_async(self, max_articles: int = 5) -> List[Dict[str, str]]:
        articles = []
        try:
            response_text = await safe_request_async(self.base_url)
            if not response_text:
                return articles
            
            soup = BeautifulSoup(response_text, 'html.parser')
            news_items = self._find_news_items(soup, max_articles)
            
            # 병렬로 기사 콘텐츠 추출
            tasks = []
            for item in news_items:
                title = self._extract_title(item)
                link = self._extract_link(item)
                if title and link:
                    tasks.append(self._extract_article_async(title, link))
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for result in results:
                    if isinstance(result, dict):
                        articles.append(result)
                    elif isinstance(result, Exception):
                        self.logger.error(f"{self.source_name} 기사 처리 중 오류: {result}")
                    
        except Exception as e:
            self.logger.error(f"{self.source_name} 크롤링 중 오류: {e}")
        
        self.logger.info(f"{self.source_name}: {len(articles)} articles found")
        return articles
    
    def _find_news_items(self, soup: BeautifulSoup, max_articles: int) -> List[Any]:
        selectors = ['article', '.post', '.article', '.entry']
        for selector in selectors:
            items = soup.select(selector)
            if items:
                return items[:max_articles]
        return []
    
    def _extract_article_data(self, item: Any) -> Optional[Dict[str, str]]:
        title = self._extract_title(item)
        if not title:
            return None
        
        link = self._extract_link(item)
        if not link:
            return None
        
        content = self._extract_content(link)
        if not content:
            content = f"제목: {title}\n\n내용을 가져올 수 없습니다."
        
        return {
            'title': title,
            'content': content,
            'url': link,
            'source': self.source_name.lower()
        }
    
    def _extract_title(self, item: Any) -> Optional[str]:
        title_selectors = ['h2', 'h3', '.title', '.entry-title']
        for selector in title_selectors:
            title_elem = item.select_one(selector)
            if title_elem:
                return title_elem.text.strip()
        return None
    
    def _extract_link(self, item: Any) -> Optional[str]:
        link_elem = item.select_one('a')
        if not link_elem or 'href' not in link_elem.attrs:
            return None
        
        link = link_elem['href']
        if not link.startswith('http'):
            link = self.base_url + link
        
        return link
    
    def _extract_content(self, url: str) -> Optional[str]:
        try:
            response = safe_request(url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            content_selectors = ['article', '.post-content', '.entry-content', '.article-content']
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    for tag in content_elem.select('.advertisement, .related-posts, .comments, .social-share'):
                        tag.decompose()
                    return content_elem.text.strip()
            
            return None
        except Exception as e:
            self.logger.error(f"본문 추출 중 오류: {e}")
            return None
    
    async def _extract_content_async(self, url: str) -> Optional[str]:
        try:
            response_text = await safe_request_async(url)
            if not response_text:
                return None
            
            soup = BeautifulSoup(response_text, 'html.parser')
            content_selectors = ['article', '.post-content', '.entry-content', '.article-content']
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    for tag in content_elem.select('.advertisement, .related-posts, .comments, .social-share'):
                        tag.decompose()
                    return content_elem.text.strip()
            
            return None
        except Exception as e:
            self.logger.error(f"본문 추출 중 오류: {e}")
            return None
    
    async def _extract_article_async(self, title: str, link: str) -> Dict[str, str]:
        content = await self._extract_content_async(link)
        if not content:
            content = f"제목: {title}\n\n내용을 가져올 수 없습니다."
        
        return {
            'title': title,
            'content': content,
            'url': link,
            'source': self.source_name.lower()
        }


class NineToFiveMacScraper(NewsScraperBase):
    def __init__(self):
        super().__init__("https://9to5mac.com", "9to5mac")


class MacRumorsScraper(NewsScraperBase):
    def __init__(self):
        super().__init__("https://www.macrumors.com", "macrumors")


def fetch_9to5mac_news() -> List[Dict[str, str]]:
    scraper = NineToFiveMacScraper()
    return scraper.scrape_news()


def fetch_macrumors_news() -> List[Dict[str, str]]:
    scraper = MacRumorsScraper()
    return scraper.scrape_news()


async def fetch_9to5mac_news_async() -> List[Dict[str, str]]:
    scraper = NineToFiveMacScraper()
    return await scraper.scrape_news_async()


async def fetch_macrumors_news_async() -> List[Dict[str, str]]:
    scraper = MacRumorsScraper()
    return await scraper.scrape_news_async()