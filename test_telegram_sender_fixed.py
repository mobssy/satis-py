import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from telegram_sender import send_telegram_message, test_bot, MAX_MESSAGE_LENGTH


class TestTelegramSender:
    
    @pytest.mark.asyncio
    @patch('telegram_sender.Bot')
    async def test_send_telegram_message_short(self, mock_bot_class):
        mock_bot = AsyncMock()
        mock_bot_class.return_value = mock_bot
        
        message = "Short test message"
        
        await send_telegram_message(message)
        
        mock_bot.send_message.assert_called_once_with(
            chat_id="7417432162",
            text=message,
            parse_mode='MarkdownV2'
        )
    
    @pytest.mark.asyncio
    @patch('telegram_sender.Bot')
    @patch('telegram_sender.asyncio.sleep')
    async def test_send_telegram_message_long(self, mock_sleep, mock_bot_class):
        mock_bot = AsyncMock()
        mock_bot_class.return_value = mock_bot
        
        # Create a message longer than MAX_MESSAGE_LENGTH
        long_message = "A" * (MAX_MESSAGE_LENGTH + 100)
        
        await send_telegram_message(long_message)
        
        # Should be called multiple times for long messages
        assert mock_bot.send_message.call_count >= 2
        mock_sleep.assert_called()
    
    @pytest.mark.asyncio
    @patch('telegram_sender.Bot')
    @patch('telegram_sender.asyncio.sleep')
    async def test_send_telegram_message_multipart(self, mock_sleep, mock_bot_class):
        mock_bot = AsyncMock()
        mock_bot_class.return_value = mock_bot
        
        # Create message with multiple lines that exceeds limit
        lines = ["Line " + str(i) for i in range(1000)]
        long_message = "\n".join(lines)
        
        await send_telegram_message(long_message)
        
        # Verify multiple calls were made
        assert mock_bot.send_message.call_count >= 2
        
        # Verify first message has part indicator
        first_call = mock_bot.send_message.call_args_list[0]
        assert "[1/" in first_call[1]['text']
    
    @pytest.mark.asyncio
    @patch('telegram_sender.Bot')
    async def test_send_telegram_message_exception(self, mock_bot_class):
        mock_bot = AsyncMock()
        mock_bot.send_message.side_effect = Exception("Send error")
        mock_bot_class.return_value = mock_bot
        
        with patch('telegram_sender.logger') as mock_logger:
            await send_telegram_message("Test message")
            
            mock_logger.error.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('telegram_sender.Bot')
    async def test_test_bot_success(self, mock_bot_class):
        mock_bot = AsyncMock()
        mock_bot_class.return_value = mock_bot
        
        # Mock bot info
        mock_bot_info = Mock()
        mock_bot_info.first_name = "Test Bot"
        mock_bot_info.username = "testbot"
        mock_bot.get_me.return_value = mock_bot_info
        
        # Mock updates with message
        mock_update = Mock()
        mock_message = Mock()
        mock_message.chat_id = 12345
        mock_message.text = "Test message"
        mock_update.message = mock_message
        mock_bot.get_updates.return_value = [mock_update]
        
        with patch('telegram_sender.logger') as mock_logger:
            await test_bot()
            
            mock_bot.get_me.assert_called_once()
            mock_bot.get_updates.assert_called_once()
            mock_logger.info.assert_called()
    
    @pytest.mark.asyncio
    @patch('telegram_sender.Bot')
    async def test_test_bot_no_updates(self, mock_bot_class):
        mock_bot = AsyncMock()
        mock_bot_class.return_value = mock_bot
        
        # Mock bot info
        mock_bot_info = Mock()
        mock_bot_info.first_name = "Test Bot"
        mock_bot_info.username = "testbot"
        mock_bot.get_me.return_value = mock_bot_info
        
        # No updates
        mock_bot.get_updates.return_value = []
        
        with patch('telegram_sender.logger') as mock_logger:
            await test_bot()
            
            mock_logger.info.assert_called()
            # Should log about no recent conversations
            error_calls = [call for call in mock_logger.info.call_args_list 
                          if "최근 대화 내역이 없습니다" in str(call)]
            assert len(error_calls) > 0
    
    @pytest.mark.asyncio
    @patch('telegram_sender.Bot')
    async def test_test_bot_exception(self, mock_bot_class):
        mock_bot_class.side_effect = Exception("Bot error")
        
        with patch('telegram_sender.logger') as mock_logger:
            await test_bot()
            
            mock_logger.error.assert_called_once()
    
    def test_max_message_length_constant(self):
        assert MAX_MESSAGE_LENGTH == 4096
    
    @pytest.mark.asyncio
    @patch('telegram_sender.Bot')
    async def test_send_telegram_message_exact_limit(self, mock_bot_class):
        mock_bot = AsyncMock()
        mock_bot_class.return_value = mock_bot
        
        # Message exactly at the limit
        message = "A" * MAX_MESSAGE_LENGTH
        
        await send_telegram_message(message)
        
        # Should send as single message
        mock_bot.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('telegram_sender.Bot')
    async def test_send_telegram_message_line_splitting(self, mock_bot_class):
        mock_bot = AsyncMock()
        mock_bot_class.return_value = mock_bot
        
        # Create message where line splitting is needed
        long_line = "A" * (MAX_MESSAGE_LENGTH - 100)
        short_line = "B" * 200
        message = long_line + "\n" + short_line
        
        await send_telegram_message(message)
        
        # Should be split into multiple messages
        assert mock_bot.send_message.call_count >= 2


if __name__ == "__main__":
    pytest.main([__file__])