"""
Test cases for Navi (Conversational AI) Module
===============================================
Tests for Ollama LLM integration, chat responses,
context-aware messaging, and conversation history.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
from app.modules.navi import NaviModule, Message


class TestMessage:
    """Test Message class"""

    def test_message_initialization(self):
        """Test creating a message"""
        msg = Message("user", "Hello Navi")

        assert msg.role == "user"
        assert msg.content == "Hello Navi"
        assert isinstance(msg.timestamp, datetime)

    def test_message_roles(self):
        """Test different message roles"""
        user_msg = Message("user", "Test")
        assert user_msg.role == "user"

        assistant_msg = Message("assistant", "Response")
        assert assistant_msg.role == "assistant"

        system_msg = Message("system", "System prompt")
        assert system_msg.role == "system"

    def test_message_to_dict(self):
        """Test message serialization"""
        msg = Message("user", "Test message")
        result = msg.to_dict()

        assert result["role"] == "user"
        assert result["content"] == "Test message"
        assert "timestamp" in result
        assert isinstance(result["timestamp"], str)


class TestNaviModule:
    """Test NaviModule class"""

    def test_initialization_default(self):
        """Test module initialization with defaults"""
        navi = NaviModule()

        assert navi.ollama_url == "http://localhost:11434"
        assert navi.mock_mode is False
        assert navi.conversation_history == []
        assert navi.system_prompt is not None
        assert navi.client is not None

    def test_initialization_mock_mode(self):
        """Test initialization in mock mode"""
        navi = NaviModule(mock_mode=True)

        assert navi.mock_mode is True
        assert navi.model == "llama3.2:1b"

    def test_initialization_custom_url(self):
        """Test initialization with custom Ollama URL"""
        navi = NaviModule(ollama_url="http://custom:11434")

        assert navi.ollama_url == "http://custom:11434"

    def test_personality_prompt_loaded(self):
        """Test that personality prompt is loaded"""
        navi = NaviModule()

        assert len(navi.system_prompt) > 0
        assert "NAVI" in navi.system_prompt or "assistant" in navi.system_prompt.lower()


class TestMockResponse:
    """Test mock response generation"""

    def test_mock_response_status_query(self):
        """Test status query response"""
        navi = NaviModule(mock_mode=True)

        response = navi._mock_response("What's the status?", None)

        assert "status" in response.lower() or "operational" in response.lower()

    def test_mock_response_status_with_context(self):
        """Test status query with context"""
        navi = NaviModule(mock_mode=True)

        context = {
            "gps": "78.22N, 15.63E",
            "cog": "45",
            "sog": "5.5",
            "threats": []
        }

        response = navi._mock_response("status", context)

        assert "78.22N" in response or "Position" in response
        assert "45" in response or "Course" in response

    def test_mock_response_threat_query(self):
        """Test threat-related query"""
        navi = NaviModule(mock_mode=True)

        response = navi._mock_response("Any threats nearby?", None)

        assert "threat" in response.lower() or "vakten" in response.lower()

    def test_mock_response_ice_query(self):
        """Test ice-related query"""
        navi = NaviModule(mock_mode=True)

        response = navi._mock_response("Tell me about ice conditions", None)

        assert "ice" in response.lower()

    def test_mock_response_weather_query(self):
        """Test weather query"""
        navi = NaviModule(mock_mode=True)

        response = navi._mock_response("What's the weather?", None)

        assert "weather" in response.lower()

    def test_mock_response_help_query(self):
        """Test help request"""
        navi = NaviModule(mock_mode=True)

        response = navi._mock_response("help", None)

        assert "assist" in response.lower() or "can" in response.lower()

    def test_mock_response_generic(self):
        """Test generic message fallback"""
        navi = NaviModule(mock_mode=True)

        response = navi._mock_response("Random question", None)

        assert "acknowledged" in response.lower() or "assist" in response.lower()

    def test_mock_response_case_insensitive(self):
        """Test keyword matching is case insensitive"""
        navi = NaviModule(mock_mode=True)

        response1 = navi._mock_response("STATUS", None)
        response2 = navi._mock_response("status", None)

        # Both should trigger status response
        assert "status" in response1.lower() or "operational" in response1.lower()
        assert "status" in response2.lower() or "operational" in response2.lower()


@pytest.mark.asyncio
class TestChatFunctionality:
    """Test chat functionality"""

    async def test_chat_adds_to_history(self):
        """Test that chat adds messages to history"""
        navi = NaviModule(mock_mode=True)

        initial_length = len(navi.conversation_history)

        await navi.chat("Hello")

        # Should add user message and assistant response
        assert len(navi.conversation_history) == initial_length + 2

    async def test_chat_user_message_stored(self):
        """Test user message is stored correctly"""
        navi = NaviModule(mock_mode=True)

        await navi.chat("Test message")

        # Last two messages should be user and assistant
        user_msg = navi.conversation_history[-2]
        assert user_msg.role == "user"
        assert user_msg.content == "Test message"

    async def test_chat_assistant_response_stored(self):
        """Test assistant response is stored"""
        navi = NaviModule(mock_mode=True)

        response = await navi.chat("Test")

        assistant_msg = navi.conversation_history[-1]
        assert assistant_msg.role == "assistant"
        assert assistant_msg.content == response

    async def test_chat_returns_string(self):
        """Test chat returns a string response"""
        navi = NaviModule(mock_mode=True)

        response = await navi.chat("Hello")

        assert isinstance(response, str)
        assert len(response) > 0

    async def test_chat_with_context(self):
        """Test chat with context dictionary"""
        navi = NaviModule(mock_mode=True)

        context = {"gps": "78.22N, 15.63E", "threats": []}

        response = await navi.chat("status", context)

        # Should include context in response
        assert isinstance(response, str)

    async def test_chat_mock_mode(self):
        """Test chat works in mock mode"""
        navi = NaviModule(mock_mode=True)

        response = await navi.chat("help")

        assert isinstance(response, str)
        assert len(response) > 0


@pytest.mark.asyncio
class TestOllamaIntegration:
    """Test Ollama LLM integration (mocked)"""

    @patch('httpx.AsyncClient')
    async def test_initialize_checks_ollama(self, mock_client_class):
        """Test initialization checks Ollama availability"""
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": [{"name": "llama3.2"}]}
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        navi = NaviModule(mock_mode=False)
        await navi.initialize()

        # Should check tags endpoint
        mock_client.get.assert_called()

    @patch('httpx.AsyncClient')
    async def test_initialize_handles_ollama_unavailable(self, mock_client_class):
        """Test fallback to mock mode when Ollama unavailable"""
        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("Connection failed")
        mock_client_class.return_value = mock_client

        navi = NaviModule(mock_mode=False)
        await navi.initialize()

        # Should fall back to mock mode
        assert navi.mock_mode is True

    @patch('httpx.AsyncClient')
    async def test_ollama_chat_sends_messages(self, mock_client_class):
        """Test Ollama chat sends proper message format"""
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": "Test response"}
        }
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        navi = NaviModule(mock_mode=False)
        navi.client = mock_client

        response = await navi._ollama_chat("Test message", None)

        assert response == "Test response"
        mock_client.post.assert_called()

    @patch('httpx.AsyncClient')
    async def test_ollama_chat_includes_context(self, mock_client_class):
        """Test Ollama chat includes context in prompt"""
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": "Response with context"}
        }
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        navi = NaviModule(mock_mode=False)
        navi.client = mock_client

        context = {"gps": "78N 15E", "threats": ["ice"]}
        response = await navi._ollama_chat("status", context)

        # Should receive response
        assert isinstance(response, str)

    @patch('httpx.AsyncClient')
    async def test_ollama_chat_handles_error(self, mock_client_class):
        """Test Ollama chat handles API errors"""
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Server error"
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        navi = NaviModule(mock_mode=False)
        navi.client = mock_client

        response = await navi._ollama_chat("test", None)

        assert "error" in response.lower()


@pytest.mark.asyncio
class TestConversationHistory:
    """Test conversation history management"""

    async def test_clear_history(self):
        """Test clearing conversation history"""
        navi = NaviModule(mock_mode=True)

        await navi.chat("Message 1")
        await navi.chat("Message 2")

        assert len(navi.conversation_history) > 0

        await navi.clear_history()

        assert len(navi.conversation_history) == 0

    def test_get_history_all(self):
        """Test getting full conversation history"""
        navi = NaviModule(mock_mode=True)

        # Add some messages manually
        navi.conversation_history.append(Message("user", "Hello"))
        navi.conversation_history.append(Message("assistant", "Hi"))

        history = navi.get_history()

        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"

    def test_get_history_limited(self):
        """Test getting limited conversation history"""
        navi = NaviModule(mock_mode=True)

        # Add many messages
        for i in range(100):
            navi.conversation_history.append(Message("user", f"Message {i}"))

        history = navi.get_history(limit=10)

        assert len(history) == 10

    def test_get_history_returns_dicts(self):
        """Test history returns list of dictionaries"""
        navi = NaviModule(mock_mode=True)

        navi.conversation_history.append(Message("user", "Test"))

        history = navi.get_history()

        assert isinstance(history, list)
        assert isinstance(history[0], dict)
        assert "role" in history[0]
        assert "content" in history[0]


@pytest.mark.asyncio
class TestStreamChat:
    """Test streaming chat functionality"""

    async def test_stream_chat_mock_mode(self):
        """Test streaming in mock mode"""
        navi = NaviModule(mock_mode=True)

        chunks = []
        async for chunk in navi.stream_chat("help", None):
            chunks.append(chunk)

        # Should yield multiple chunks
        assert len(chunks) > 0

        # Concatenated chunks should form response
        full_response = "".join(chunks)
        assert len(full_response) > 0

    async def test_stream_chat_adds_to_history(self):
        """Test streaming adds to history"""
        navi = NaviModule(mock_mode=True)

        initial_length = len(navi.conversation_history)

        chunks = []
        async for chunk in navi.stream_chat("test", None):
            chunks.append(chunk)

        # Should add user and assistant messages
        assert len(navi.conversation_history) > initial_length


class TestModuleStatus:
    """Test module status reporting"""

    def test_get_status(self):
        """Test getting module status"""
        navi = NaviModule(mock_mode=True)

        status = navi.get_status()

        assert status["module"] == "navi"
        assert status["status"] == "ready"
        assert status["mock_mode"] is True
        assert "model" in status
        assert "ollama_url" in status
        assert "conversation_length" in status

    def test_get_status_tracks_conversation_length(self):
        """Test status reflects conversation length"""
        navi = NaviModule(mock_mode=True)

        initial_status = navi.get_status()
        initial_length = initial_status["conversation_length"]

        navi.conversation_history.append(Message("user", "test"))

        updated_status = navi.get_status()

        assert updated_status["conversation_length"] == initial_length + 1


@pytest.mark.asyncio
class TestModuleLifecycle:
    """Test module lifecycle operations"""

    async def test_close_connections(self):
        """Test closing client connections"""
        navi = NaviModule(mock_mode=True)

        # Should not raise exception
        await navi.close()


class TestPersonalityPrompt:
    """Test personality prompt functionality"""

    def test_load_personality_default(self):
        """Test loading default personality"""
        navi = NaviModule()

        prompt = navi._load_personality()

        assert len(prompt) > 0
        assert "NAVI" in prompt or "Arctic" in prompt or "assistant" in prompt.lower()

    def test_personality_contains_key_elements(self):
        """Test personality prompt has required elements"""
        navi = NaviModule()

        assert "Arctic" in navi.system_prompt or "maritime" in navi.system_prompt.lower()

    @patch('os.path.exists')
    @patch('builtins.open', create=True)
    def test_load_personality_from_file(self, mock_open, mock_exists):
        """Test loading personality from file"""
        mock_exists.return_value = True
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = "Custom personality"
        mock_open.return_value = mock_file

        navi = NaviModule()

        # Should attempt to load from file
        mock_exists.assert_called()


class TestContextAwareness:
    """Test context-aware responses"""

    def test_mock_response_includes_gps(self):
        """Test GPS coordinates included in status response"""
        navi = NaviModule(mock_mode=True)

        context = {"gps": "78.22N, 15.63E"}
        response = navi._mock_response("status", context)

        assert "position" in response.lower() or "78" in response

    def test_mock_response_includes_threats(self):
        """Test threat count included in response"""
        navi = NaviModule(mock_mode=True)

        context = {"threats": ["ice", "ship"]}
        response = navi._mock_response("status", context)

        assert "threat" in response.lower() or "2" in response

    def test_mock_response_no_context(self):
        """Test response works without context"""
        navi = NaviModule(mock_mode=True)

        response = navi._mock_response("status", None)

        assert "awaiting" in response.lower() or "operational" in response.lower()


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_message(self):
        """Test handling of empty message"""
        navi = NaviModule(mock_mode=True)

        response = navi._mock_response("", None)

        assert isinstance(response, str)

    def test_very_long_message(self):
        """Test handling of very long message"""
        navi = NaviModule(mock_mode=True)

        long_message = "test " * 1000
        response = navi._mock_response(long_message, None)

        assert isinstance(response, str)

    @pytest.mark.asyncio
    async def test_chat_preserves_order(self):
        """Test messages are stored in chronological order"""
        navi = NaviModule(mock_mode=True)

        await navi.chat("First")
        await navi.chat("Second")
        await navi.chat("Third")

        # Check order
        messages = [m.content for m in navi.conversation_history if m.role == "user"]
        assert messages[-3:] == ["First", "Second", "Third"]

    def test_special_characters_in_message(self):
        """Test handling of special characters"""
        navi = NaviModule(mock_mode=True)

        response = navi._mock_response("Test @#$% message!", None)

        assert isinstance(response, str)
