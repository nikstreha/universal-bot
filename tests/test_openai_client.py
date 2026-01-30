import pytest
import uuid

from openai import AuthenticationError

from unittest.mock import AsyncMock, MagicMock, patch

from src.clients.openai import OpenAIClient
from src.schemas.chat import RequestSchema, HistorySchema, MessageSchema, MessageRole, ResponseSchema

@pytest.fixture
def openai_client():
    return OpenAIClient()

@pytest.mark.asyncio
async def test_embedding_success(openai_client):
    mock_response = MagicMock()
    mock_data = MagicMock()
    mock_data.embedding = [0.1, 0.2, 0.3]
    mock_response.data = [mock_data]
    
    with patch.object(openai_client.client.embeddings, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        
        result = await openai_client.embedding("test text")
        
        assert result == [0.1, 0.2, 0.3]
        mock_create.assert_called_once()

@pytest.mark.asyncio
async def test_embedding_empty_text(openai_client):
    result = await openai_client.embedding("  ")
    assert result is None

@pytest.mark.asyncio
async def test_generate_success(openai_client):
    user_id = uuid.uuid4()
    request = RequestSchema(user_id=user_id, content="Hello", temperature=0.7, max_tokens=100)
    history = HistorySchema(messages=[MessageSchema(role=MessageRole.USER, content="Hi")])
    
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Hello there!"
    mock_response.choices = [mock_choice]
    mock_response.usage.total_tokens = 15
    
    with patch.object(openai_client.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        
        result = await openai_client.generate(request, history)
        
        assert isinstance(result, ResponseSchema)
        assert result.user_id == user_id
        assert result.content == "Hello there!"
        assert result.tokens_used == 15
        mock_create.assert_called_once()

@pytest.mark.asyncio
async def test_invalid_token_error(openai_client): 
    with patch.object(openai_client.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = AuthenticationError(
            "Incorrect API key provided", 
            response=MagicMock(status_code=401),
            body={"message": "Incorrect API key provided"}
        )
        
        user_id = uuid.uuid4()
        request = RequestSchema(user_id=user_id, content="Hello")
        history = HistorySchema(messages=[])
        
        with pytest.raises(AuthenticationError) as excinfo:
            await openai_client.generate(request, history)
        
        assert "API key" in str(excinfo.value) or "token" in str(excinfo.value).lower()
