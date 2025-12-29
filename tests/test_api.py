"""Tests for feishu_sdk.api module."""

import os

import httpx
import pytest
import responses
import respx

from feishu_sdk.api import AsyncMessageApiClient, LarkException, MessageApiClient


class TestMessageApiClient:
    """Tests for the MessageApiClient class."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return MessageApiClient(
            app_id="test_app_id", app_secret="test_app_secret", lark_host="https://open.feishu.cn"
        )

    def test_init(self, client):
        """Test client initialization."""
        assert client._app_id == "test_app_id"
        assert client._app_secret == "test_app_secret"
        assert client._lark_host == "https://open.feishu.cn"
        assert client._tenant_access_token == ""

    def test_tenant_access_token_property(self, client):
        """Test tenant_access_token property."""
        client._tenant_access_token = "test_token"
        assert client.tenant_access_token == "test_token"

    def test_from_env_success(self, monkeypatch):
        """Test creating client from environment variables."""
        monkeypatch.setenv("APP_ID", "env_app_id")
        monkeypatch.setenv("APP_SECRET", "env_app_secret")

        client = MessageApiClient.from_env("https://open.feishu.cn")
        assert client._app_id == "env_app_id"
        assert client._app_secret == "env_app_secret"

    def test_from_env_custom_vars(self, monkeypatch):
        """Test from_env with custom variable names."""
        monkeypatch.setenv("MY_APP_ID", "custom_id")
        monkeypatch.setenv("MY_APP_SECRET", "custom_secret")

        client = MessageApiClient.from_env(
            "https://open.feishu.cn", app_id_env="MY_APP_ID", app_secret_env="MY_APP_SECRET"
        )
        assert client._app_id == "custom_id"
        assert client._app_secret == "custom_secret"

    def test_from_env_missing_app_id(self, monkeypatch):
        """Test from_env raises error when APP_ID is missing."""
        monkeypatch.delenv("APP_ID", raising=False)
        monkeypatch.setenv("APP_SECRET", "secret")

        with pytest.raises(ValueError) as exc_info:
            MessageApiClient.from_env("https://open.feishu.cn")
        assert "APP_ID" in str(exc_info.value)

    def test_from_env_missing_app_secret(self, monkeypatch):
        """Test from_env raises error when APP_SECRET is missing."""
        monkeypatch.setenv("APP_ID", "id")
        monkeypatch.delenv("APP_SECRET", raising=False)

        with pytest.raises(ValueError) as exc_info:
            MessageApiClient.from_env("https://open.feishu.cn")
        assert "APP_SECRET" in str(exc_info.value)

    @responses.activate
    def test_authorize_tenant_access_token(self, client):
        """Test tenant access token authorization."""
        responses.add(
            responses.POST,
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={"code": 0, "tenant_access_token": "new_token"},
            status=200,
        )

        client._authorize_tenant_access_token()
        assert client._tenant_access_token == "new_token"

    @responses.activate
    def test_authorize_tenant_access_token_error(self, client):
        """Test tenant access token authorization with API error."""
        responses.add(
            responses.POST,
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={"code": 99991, "msg": "invalid app_id"},
            status=200,
        )

        with pytest.raises(LarkException) as exc_info:
            client._authorize_tenant_access_token()
        assert exc_info.value.code == 99991

    @responses.activate
    def test_send_text_with_open_id(self, client):
        """Test sending text message."""
        # Mock token endpoint
        responses.add(
            responses.POST,
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={"code": 0, "tenant_access_token": "test_token"},
            status=200,
        )
        # Mock message endpoint
        responses.add(
            responses.POST,
            "https://open.feishu.cn/open-apis/im/v1/messages",
            json={"code": 0, "data": {"message_id": "msg_123"}},
            status=200,
        )

        client.send_text_with_open_id("ou_123", "Hello World")

        # Verify the message request was made
        assert len(responses.calls) == 2
        message_call = responses.calls[1]
        assert "receive_id_type=open_id" in message_call.request.url

    @responses.activate
    def test_send_card_with_open_id(self, client):
        """Test sending card message."""
        responses.add(
            responses.POST,
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={"code": 0, "tenant_access_token": "test_token"},
            status=200,
        )
        responses.add(
            responses.POST,
            "https://open.feishu.cn/open-apis/im/v1/messages",
            json={"code": 0, "data": {"message_id": "msg_456"}},
            status=200,
        )

        card_content = '{"elements": []}'
        result = client.send_card_with_open_id("ou_123", card_content)
        assert result == "msg_456"

    @responses.activate
    def test_send_update_message_card(self, client):
        """Test updating a message card."""
        responses.add(
            responses.POST,
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={"code": 0, "tenant_access_token": "test_token"},
            status=200,
        )
        responses.add(
            responses.PATCH,
            "https://open.feishu.cn/open-apis/im/v1/messages/msg_123",
            json={"code": 0},
            status=200,
        )

        client.send_update_message_card("msg_123", '{"elements": []}')

        # Verify PATCH request was made
        assert len(responses.calls) == 2
        assert responses.calls[1].request.method == "PATCH"

    @responses.activate
    def test_check_error_response_http_error(self, client):
        """Test error checking with HTTP error."""
        responses.add(
            responses.POST,
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={"error": "server error"},
            status=500,
        )

        with pytest.raises(Exception):  # requests.HTTPError
            client._authorize_tenant_access_token()

    @responses.activate
    def test_check_error_response_api_error(self, client):
        """Test error checking with API-level error."""
        responses.add(
            responses.POST,
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={"code": 10001, "msg": "Invalid token"},
            status=200,
        )

        with pytest.raises(LarkException) as exc_info:
            client._authorize_tenant_access_token()
        assert exc_info.value.code == 10001
        assert exc_info.value.msg == "Invalid token"


class TestLarkException:
    """Tests for the LarkException class."""

    def test_init_defaults(self):
        """Test default initialization."""
        exc = LarkException()
        assert exc.code == 0
        assert exc.msg is None

    def test_init_with_values(self):
        """Test initialization with values."""
        exc = LarkException(code=123, msg="test message")
        assert exc.code == 123
        assert exc.msg == "test message"

    def test_str_representation(self):
        """Test string representation."""
        exc = LarkException(code=456, msg="error occurred")
        assert str(exc) == "456:error occurred"

    def test_repr_representation(self):
        """Test repr is same as str."""
        exc = LarkException(code=789, msg="test")
        assert repr(exc) == str(exc)


class TestAsyncMessageApiClient:
    """Tests for the AsyncMessageApiClient class."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return AsyncMessageApiClient(
            app_id="test_app_id", app_secret="test_app_secret", lark_host="https://open.feishu.cn"
        )

    def test_init(self, client):
        """Test client initialization."""
        assert client._app_id == "test_app_id"
        assert client._app_secret == "test_app_secret"
        assert client._lark_host == "https://open.feishu.cn"
        assert client._tenant_access_token == ""
        assert client._client is None

    def test_tenant_access_token_property(self, client):
        """Test tenant_access_token property."""
        client._tenant_access_token = "test_token"
        assert client.tenant_access_token == "test_token"

    def test_from_env_success(self, monkeypatch):
        """Test creating client from environment variables."""
        monkeypatch.setenv("APP_ID", "env_app_id")
        monkeypatch.setenv("APP_SECRET", "env_app_secret")

        client = AsyncMessageApiClient.from_env("https://open.feishu.cn")
        assert client._app_id == "env_app_id"
        assert client._app_secret == "env_app_secret"

    def test_from_env_custom_vars(self, monkeypatch):
        """Test from_env with custom variable names."""
        monkeypatch.setenv("MY_APP_ID", "custom_id")
        monkeypatch.setenv("MY_APP_SECRET", "custom_secret")

        client = AsyncMessageApiClient.from_env(
            "https://open.feishu.cn", app_id_env="MY_APP_ID", app_secret_env="MY_APP_SECRET"
        )
        assert client._app_id == "custom_id"
        assert client._app_secret == "custom_secret"

    def test_from_env_missing_app_id(self, monkeypatch):
        """Test from_env raises error when APP_ID is missing."""
        monkeypatch.delenv("APP_ID", raising=False)
        monkeypatch.setenv("APP_SECRET", "secret")

        with pytest.raises(ValueError) as exc_info:
            AsyncMessageApiClient.from_env("https://open.feishu.cn")
        assert "APP_ID" in str(exc_info.value)

    def test_from_env_missing_app_secret(self, monkeypatch):
        """Test from_env raises error when APP_SECRET is missing."""
        monkeypatch.setenv("APP_ID", "id")
        monkeypatch.delenv("APP_SECRET", raising=False)

        with pytest.raises(ValueError) as exc_info:
            AsyncMessageApiClient.from_env("https://open.feishu.cn")
        assert "APP_SECRET" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_context_manager(self, client):
        """Test async context manager entry and exit."""
        assert client._client is None

        async with client:
            assert client._client is not None
            assert isinstance(client._client, httpx.AsyncClient)

        assert client._client is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_authorize_tenant_access_token(self, client):
        """Test tenant access token authorization."""
        respx.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal").mock(
            return_value=httpx.Response(200, json={"code": 0, "tenant_access_token": "new_token"})
        )

        async with client:
            await client._authorize_tenant_access_token()
            assert client._tenant_access_token == "new_token"

    @pytest.mark.asyncio
    @respx.mock
    async def test_authorize_tenant_access_token_error(self, client):
        """Test tenant access token authorization with API error."""
        respx.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal").mock(
            return_value=httpx.Response(200, json={"code": 99991, "msg": "invalid app_id"})
        )

        async with client:
            with pytest.raises(LarkException) as exc_info:
                await client._authorize_tenant_access_token()
            assert exc_info.value.code == 99991

    @pytest.mark.asyncio
    @respx.mock
    async def test_send_text_with_open_id(self, client):
        """Test sending text message."""
        # Mock token endpoint
        respx.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal").mock(
            return_value=httpx.Response(200, json={"code": 0, "tenant_access_token": "test_token"})
        )
        # Mock message endpoint
        respx.post(url__regex=r".*/open-apis/im/v1/messages\?.*").mock(
            return_value=httpx.Response(200, json={"code": 0, "data": {"message_id": "msg_123"}})
        )

        async with client:
            result = await client.send_text_with_open_id("ou_123", "Hello World")
            assert result == "msg_123"

    @pytest.mark.asyncio
    @respx.mock
    async def test_send_card_with_open_id(self, client):
        """Test sending card message."""
        respx.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal").mock(
            return_value=httpx.Response(200, json={"code": 0, "tenant_access_token": "test_token"})
        )
        respx.post(url__regex=r".*/open-apis/im/v1/messages\?.*").mock(
            return_value=httpx.Response(200, json={"code": 0, "data": {"message_id": "msg_456"}})
        )

        async with client:
            card_content = '{"elements": []}'
            result = await client.send_card_with_open_id("ou_123", card_content)
            assert result == "msg_456"

    @pytest.mark.asyncio
    @respx.mock
    async def test_send_update_message_card(self, client):
        """Test updating a message card."""
        respx.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal").mock(
            return_value=httpx.Response(200, json={"code": 0, "tenant_access_token": "test_token"})
        )
        respx.patch("https://open.feishu.cn/open-apis/im/v1/messages/msg_123").mock(
            return_value=httpx.Response(200, json={"code": 0})
        )

        async with client:
            await client.send_update_message_card("msg_123", '{"elements": []}')

    @pytest.mark.asyncio
    @respx.mock
    async def test_check_error_response_http_error(self, client):
        """Test error checking with HTTP error."""
        respx.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal").mock(
            return_value=httpx.Response(500, json={"error": "server error"})
        )

        async with client:
            with pytest.raises(httpx.HTTPStatusError):
                await client._authorize_tenant_access_token()

    @pytest.mark.asyncio
    @respx.mock
    async def test_check_error_response_api_error(self, client):
        """Test error checking with API-level error."""
        respx.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal").mock(
            return_value=httpx.Response(200, json={"code": 10001, "msg": "Invalid token"})
        )

        async with client:
            with pytest.raises(LarkException) as exc_info:
                await client._authorize_tenant_access_token()
            assert exc_info.value.code == 10001
            assert exc_info.value.msg == "Invalid token"

    @pytest.mark.asyncio
    @respx.mock
    async def test_without_context_manager(self, client):
        """Test that client works without context manager."""
        respx.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal").mock(
            return_value=httpx.Response(200, json={"code": 0, "tenant_access_token": "test_token"})
        )
        respx.post(url__regex=r".*/open-apis/im/v1/messages\?.*").mock(
            return_value=httpx.Response(200, json={"code": 0, "data": {"message_id": "msg_789"}})
        )

        # Should work without async context manager (creates temporary client)
        result = await client.send_text_with_open_id("ou_123", "Hello")
        assert result == "msg_789"
