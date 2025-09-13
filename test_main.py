import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import pytz
from main import TimeManager, MessageFormatter, NewsCollector, NewsDistributor, NewsOrchestrator


class TestTimeManager:
    
    def test_get_current_time_success(self):
        result = TimeManager.get_current_time()
        assert isinstance(result, datetime)
    
    @patch('main.pytz.timezone')
    def test_get_current_time_error(self, mock_timezone):
        mock_timezone.side_effect = Exception("Timezone error")
        
        with patch('main.logging.getLogger') as mock_logger:
            mock_log = Mock()
            mock_logger.return_value = mock_log
            
            result = TimeManager.get_current_time()
            assert isinstance(result, datetime)
            mock_log.error.assert_called_once()
    
    @patch.object(TimeManager, 'get_current_time')
    def test_is_tuesday_true(self, mock_get_time):
        mock_time = Mock()
        mock_time.weekday.return_value = 1  # Tuesday
        mock_get_time.return_value = mock_time
        
        assert TimeManager.is_tuesday() is True
    
    @patch.object(TimeManager, 'get_current_time')
    def test_is_tuesday_false(self, mock_get_time):
        mock_time = Mock()
        mock_time.weekday.return_value = 0  # Monday
        mock_get_time.return_value = mock_time
        
        assert TimeManager.is_tuesday() is False


class TestMessageFormatter:
    
    def test_escape_markdown_v2_none(self):
        result = MessageFormatter.escape_markdown_v2(None)
        assert result == ""
    
    def test_escape_markdown_v2_empty(self):
        result = MessageFormatter.escape_markdown_v2("")
        assert result == ""
    
    def test_escape_markdown_v2_special_chars(self):
        text = "Hello *world* [test]"
        result = MessageFormatter.escape_markdown_v2(text)
        assert result == "Hello \\*world\\* \\[test\\]"
    
    def test_escape_markdown_v2_normal_text(self):
        text = "Hello world"
        result = MessageFormatter.escape_markdown_v2(text)
        assert result == "Hello world"
    
    @patch('main.summarize_article')
    def test_create_news_message_success(self, mock_summarize):
        mock_summarize.return_value = "Test summary"
        news_list = [
            {'title': 'Test Title', 'content': 'Test content', 'url': 'http://test.com'},
            {'title': 'Test Title', 'content': 'Duplicate', 'url': 'http://test2.com'}  # Duplicate title
        ]
        
        result = MessageFormatter.create_news_message(news_list, "테스트", "🔥", "(2023-01-01)")
        
        assert "🔥 테스트 뉴스 업데이트 (2023-01-01)" in result
        assert "Test Title" in result
        assert "Test summary" in result
        assert "http://test\\.com" in result  # escaped dot
        # Should only appear once due to deduplication
        assert result.count("Test Title") == 1
    
    def test_create_news_message_empty_list(self):
        result = MessageFormatter.create_news_message([], "테스트", "🔥", "(2023-01-01)")
        assert result is None
    
    @patch('main.summarize_article')
    def test_create_news_message_exception_handling(self, mock_summarize):
        mock_summarize.side_effect = Exception("Summarize error")
        news_list = [{'title': 'Test Title', 'content': 'Test content', 'url': 'http://test.com'}]
        
        with patch('main.logging.getLogger') as mock_logger:
            mock_log = Mock()
            mock_logger.return_value = mock_log
            
            result = MessageFormatter.create_news_message(news_list, "테스트", "🔥", "(2023-01-01)")
            
            # Should still create message header even if article processing fails
            assert "🔥 테스트 뉴스 업데이트 (2023-01-01)" in result


class TestNewsCollector:
    
    def setup_method(self):
        self.collector = NewsCollector()
    
    @patch('main.TimeManager.is_tuesday')
    @patch('main.fetch_9to5mac_news_async')
    @patch('main.fetch_macrumors_news_async')
    async def test_collect_apple_news_tuesday(self, mock_macrumors, mock_9to5mac, mock_is_tuesday):
        mock_is_tuesday.return_value = True
        mock_9to5mac.return_value = [{'title': '9to5mac article'}] * 5
        mock_macrumors.return_value = [{'title': 'MacRumors article'}] * 5
        
        result = await self.collector.collect_apple_news()
        
        assert len(result) == 5  # 3 from 9to5mac + 2 from MacRumors
        mock_9to5mac.assert_called_once()
        mock_macrumors.assert_called_once()
    
    @patch('main.TimeManager.is_tuesday')
    async def test_collect_apple_news_not_tuesday(self, mock_is_tuesday):
        mock_is_tuesday.return_value = False
        
        result = await self.collector.collect_apple_news()
        
        assert result == []
    
    @patch('main.get_naver_news')
    @patch('main.get_nate_news')
    async def test_collect_korean_news_success(self, mock_nate, mock_naver):
        mock_naver.return_value = [{'title': 'Naver article'}] * 3
        mock_nate.return_value = [{'title': 'Nate article'}] * 4
        
        result = await self.collector.collect_korean_news()
        
        assert len(result) == 5  # Limited to 5
        mock_naver.assert_called_once()
        mock_nate.assert_called_once()
    
    @patch('main.get_naver_news')
    @patch('main.get_nate_news')
    async def test_collect_korean_news_exception(self, mock_nate, mock_naver):
        mock_naver.side_effect = Exception("Naver error")
        mock_nate.side_effect = Exception("Nate error")
        
        result = await self.collector.collect_korean_news()
        
        assert result == []


class TestNewsDistributor:
    
    def setup_method(self):
        self.distributor = NewsDistributor()
    
    @patch('main.send_telegram_message')
    async def test_send_news_safely_success(self, mock_send):
        mock_send.return_value = None
        
        await self.distributor.send_news_safely("Test message", "테스트")
        
        mock_send.assert_called_once_with("Test message")
    
    @patch('main.send_telegram_message')
    async def test_send_news_safely_empty_message(self, mock_send):
        await self.distributor.send_news_safely(None, "테스트")
        
        mock_send.assert_not_called()
    
    @patch('main.send_telegram_message')
    async def test_send_news_safely_exception(self, mock_send):
        mock_send.side_effect = Exception("Send error")
        
        # The logger is already created in the instance, so we patch it directly
        with patch.object(self.distributor, 'logger') as mock_logger:
            await self.distributor.send_news_safely("Test message", "테스트")
            
            mock_logger.error.assert_called_once()
    
    @patch('main.TimeManager.get_current_time')
    @patch('main.MessageFormatter.create_news_message')
    async def test_distribute_news(self, mock_create_message, mock_get_time):
        mock_time = Mock()
        mock_time.strftime.return_value = "2023년 01월 01일 12시 00분"
        mock_get_time.return_value = mock_time
        
        mock_create_message.return_value = "Test message"
        
        news_data = {
            'apple': [{'title': 'Apple news'}],
            'korean': [],
            'world': [{'title': 'World news'}],
            'us': [],
            'bigtech': []
        }
        
        with patch.object(self.distributor, 'send_news_safely') as mock_send:
            await self.distributor.distribute_news(news_data)
            
            # Should be called twice (apple and world news)
            assert mock_send.call_count == 2


class TestNewsOrchestrator:
    
    @patch('main.Logger.setup')
    def test_init(self, mock_setup):
        mock_logger = Mock()
        mock_setup.return_value = mock_logger
        
        orchestrator = NewsOrchestrator()
        
        assert isinstance(orchestrator.collector, NewsCollector)
        assert isinstance(orchestrator.distributor, NewsDistributor)
        mock_setup.assert_called_once()
    
    @patch('main.Logger.setup')
    async def test_run_success(self, mock_setup):
        mock_logger = Mock()
        mock_setup.return_value = mock_logger
        
        orchestrator = NewsOrchestrator()
        
        # Mock all collect methods
        with patch.object(orchestrator.collector, 'collect_apple_news', return_value=[]) as mock_apple, \
             patch.object(orchestrator.collector, 'collect_korean_news', return_value=[]) as mock_korean, \
             patch.object(orchestrator.collector, 'collect_world_news', return_value=[]) as mock_world, \
             patch.object(orchestrator.collector, 'collect_us_news', return_value=[]) as mock_us, \
             patch.object(orchestrator.collector, 'collect_bigtech_news', return_value=[]) as mock_bigtech, \
             patch.object(orchestrator.distributor, 'distribute_news') as mock_distribute:
            
            await orchestrator.run()
            
            # Verify all collectors were called
            mock_apple.assert_called_once()
            mock_korean.assert_called_once()
            mock_world.assert_called_once()
            mock_us.assert_called_once()
            mock_bigtech.assert_called_once()
            
            # Verify distributor was called
            mock_distribute.assert_called_once()
            
            # Verify logging
            mock_logger.info.assert_called()
    
    @patch('main.Logger.setup')
    async def test_run_exception(self, mock_setup):
        mock_logger = Mock()
        mock_setup.return_value = mock_logger
        
        orchestrator = NewsOrchestrator()
        
        # Patch all collection methods to ensure they complete but one throws error
        with patch.object(orchestrator.collector, 'collect_apple_news', side_effect=Exception("Test error")), \
             patch.object(orchestrator.collector, 'collect_korean_news', return_value=[]), \
             patch.object(orchestrator.collector, 'collect_world_news', return_value=[]), \
             patch.object(orchestrator.collector, 'collect_us_news', return_value=[]), \
             patch.object(orchestrator.collector, 'collect_bigtech_news', return_value=[]), \
             patch.object(orchestrator.distributor, 'distribute_news'):
            
            await orchestrator.run()
            
            # Should log the apple news collection error
            error_calls = [call for call in mock_logger.error.call_args_list 
                          if "apple 뉴스 수집 중 오류" in str(call)]
            assert len(error_calls) > 0


if __name__ == "__main__":
    pytest.main([__file__])