import pytest
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup
from news_scraper import NewsScraperBase, NineToFiveMacScraper, MacRumorsScraper, fetch_9to5mac_news, fetch_macrumors_news


class TestNewsScraperBase:
    
    def test_init(self):
        scraper = NewsScraperBase("http://test.com", "test")
        assert scraper.base_url == "http://test.com"
        assert scraper.source_name == "test"
    
    @patch('news_scraper.safe_request')
    def test_scrape_news_no_response(self, mock_request):
        mock_request.return_value = None
        scraper = NewsScraperBase("http://test.com", "test")
        result = scraper.scrape_news()
        assert result == []
    
    @patch('news_scraper.safe_request')
    def test_scrape_news_success(self, mock_request):
        mock_response = Mock()
        mock_response.text = '<html><article><h2>Test Title</h2><a href="/test">Link</a></article></html>'
        mock_request.return_value = mock_response
        
        scraper = NewsScraperBase("http://test.com", "test")
        
        with patch.object(scraper, '_extract_content', return_value="Test content"):
            result = scraper.scrape_news()
            assert len(result) == 1
            assert result[0]['title'] == "Test Title"
            assert result[0]['url'] == "http://test.com/test"
            assert result[0]['source'] == "test"
    
    def test_find_news_items(self):
        html = '<html><article class="post">Item 1</article><article>Item 2</article></html>'
        soup = BeautifulSoup(html, 'html.parser')
        scraper = NewsScraperBase("http://test.com", "test")
        
        items = scraper._find_news_items(soup, 5)
        assert len(items) == 2
    
    def test_extract_title_success(self):
        html = '<div><h2>Test Title</h2></div>'
        soup = BeautifulSoup(html, 'html.parser')
        item = soup.select_one('div')
        scraper = NewsScraperBase("http://test.com", "test")
        
        title = scraper._extract_title(item)
        assert title == "Test Title"
    
    def test_extract_title_no_title(self):
        html = '<div><p>No title here</p></div>'
        soup = BeautifulSoup(html, 'html.parser')
        item = soup.select_one('div')
        scraper = NewsScraperBase("http://test.com", "test")
        
        title = scraper._extract_title(item)
        assert title is None
    
    def test_extract_link_relative_url(self):
        html = '<div><a href="/test-article">Link</a></div>'
        soup = BeautifulSoup(html, 'html.parser')
        item = soup.select_one('div')
        scraper = NewsScraperBase("http://test.com", "test")
        
        link = scraper._extract_link(item)
        assert link == "http://test.com/test-article"
    
    def test_extract_link_absolute_url(self):
        html = '<div><a href="https://example.com/test">Link</a></div>'
        soup = BeautifulSoup(html, 'html.parser')
        item = soup.select_one('div')
        scraper = NewsScraperBase("http://test.com", "test")
        
        link = scraper._extract_link(item)
        assert link == "https://example.com/test"
    
    def test_extract_link_no_link(self):
        html = '<div><p>No link here</p></div>'
        soup = BeautifulSoup(html, 'html.parser')
        item = soup.select_one('div')
        scraper = NewsScraperBase("http://test.com", "test")
        
        link = scraper._extract_link(item)
        assert link is None
    
    @patch('news_scraper.safe_request')
    def test_extract_content_success(self, mock_request):
        mock_response = Mock()
        mock_response.text = '<html><article>Test content here</article></html>'
        mock_request.return_value = mock_response
        
        scraper = NewsScraperBase("http://test.com", "test")
        content = scraper._extract_content("http://test.com/article")
        
        assert "Test content here" in content
    
    @patch('news_scraper.safe_request')
    def test_extract_content_no_response(self, mock_request):
        mock_request.return_value = None
        scraper = NewsScraperBase("http://test.com", "test")
        
        content = scraper._extract_content("http://test.com/article")
        assert content is None


class TestNineToFiveMacScraper:
    
    def test_init(self):
        scraper = NineToFiveMacScraper()
        assert scraper.base_url == "https://9to5mac.com"
        assert scraper.source_name == "9to5mac"


class TestMacRumorsScraper:
    
    def test_init(self):
        scraper = MacRumorsScraper()
        assert scraper.base_url == "https://www.macrumors.com"
        assert scraper.source_name == "macrumors"


class TestScraperFunctions:
    
    @patch('news_scraper.NineToFiveMacScraper')
    def test_fetch_9to5mac_news(self, mock_scraper_class):
        mock_scraper = Mock()
        mock_scraper.scrape_news.return_value = [{'title': 'Test', 'content': 'Content', 'url': 'http://test.com', 'source': '9to5mac'}]
        mock_scraper_class.return_value = mock_scraper
        
        result = fetch_9to5mac_news()
        assert len(result) == 1
        assert result[0]['source'] == '9to5mac'
        mock_scraper.scrape_news.assert_called_once()
    
    @patch('news_scraper.MacRumorsScraper')
    def test_fetch_macrumors_news(self, mock_scraper_class):
        mock_scraper = Mock()
        mock_scraper.scrape_news.return_value = [{'title': 'Test', 'content': 'Content', 'url': 'http://test.com', 'source': 'macrumors'}]
        mock_scraper_class.return_value = mock_scraper
        
        result = fetch_macrumors_news()
        assert len(result) == 1
        assert result[0]['source'] == 'macrumors'
        mock_scraper.scrape_news.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])