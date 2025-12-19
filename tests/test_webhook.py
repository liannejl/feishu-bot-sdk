"""Tests for feishu_sdk.webhook module."""

import json
import pytest
from flask import Flask
from feishu_sdk.webhook import WebhookHandler, create_webhook_handler


class TestWebhookHandler:
    """Tests for the WebhookHandler class."""

    @pytest.fixture
    def app(self):
        """Create a test Flask app."""
        app = Flask(__name__)
        app.config["TESTING"] = True
        return app

    @pytest.fixture
    def handler(self, app):
        """Create a webhook handler with Flask app."""
        return WebhookHandler(app)

    @pytest.fixture
    def client(self, app, handler):
        """Create a test client."""
        return app.test_client()

    def test_init_without_app(self):
        """Test initialization without Flask app."""
        handler = WebhookHandler()
        assert handler.app is None
        assert handler.endpoint == "/webhook"
        assert handler.message_handlers == {}
        assert handler.event_handlers == {}

    def test_init_with_app(self, app):
        """Test initialization with Flask app."""
        handler = WebhookHandler(app)
        assert handler.app == app
        assert handler.endpoint == "/webhook"

    def test_init_custom_endpoint(self, app):
        """Test initialization with custom endpoint."""
        handler = WebhookHandler(app, endpoint="/custom")
        assert handler.endpoint == "/custom"

    def test_init_app(self, app):
        """Test init_app method."""
        handler = WebhookHandler()
        handler.init_app(app)
        assert handler.app == app
        # Verify route was added
        assert "feishu_webhook" in app.view_functions

    def test_message_handler_decorator(self, handler):
        """Test message handler decorator registration."""
        @handler.message_handler("text")
        def handle_text(event):
            pass

        assert "text" in handler.message_handlers
        assert handler.message_handlers["text"] == handle_text

    def test_message_handler_default_type(self, handler):
        """Test message handler with default type."""
        @handler.message_handler()
        def handle_default(event):
            pass

        assert "text" in handler.message_handlers

    def test_event_handler_decorator(self, handler):
        """Test event handler decorator registration."""
        @handler.event_handler("user.created")
        def handle_user_created(event):
            pass

        assert "user.created" in handler.event_handlers
        assert handler.event_handlers["user.created"] == handle_user_created

    def test_url_verification(self, client):
        """Test URL verification handling."""
        response = client.post(
            "/webhook",
            json={
                "type": "url_verification",
                "challenge": "test_challenge_123"
            },
            content_type="application/json"
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["challenge"] == "test_challenge_123"

    def test_invalid_event_returns_400(self, client):
        """Test that invalid events return 400."""
        response = client.post(
            "/webhook",
            json={"invalid": "data"},
            content_type="application/json"
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_valid_message_event(self, client, handler):
        """Test handling valid message event."""
        received_events = []

        @handler.message_handler("text")
        def handle_text(event):
            received_events.append(event)

        response = client.post(
            "/webhook",
            json={
                "header": {
                    "event_type": "im.message.receive_v1"
                },
                "event": {
                    "message": {
                        "message_type": "text",
                        "content": '{"text": "Hello"}'
                    }
                }
            },
            content_type="application/json"
        )
        assert response.status_code == 200

    def test_valid_custom_event(self, client, handler):
        """Test handling custom event type."""
        @handler.event_handler("custom.event.type")
        def handle_custom(event):
            pass

        response = client.post(
            "/webhook",
            json={
                "header": {
                    "event_type": "custom.event.type"
                },
                "event": {
                    "data": "test"
                }
            },
            content_type="application/json"
        )
        assert response.status_code == 200

    def test_unhandled_event_type(self, client):
        """Test that unhandled event types return 200."""
        response = client.post(
            "/webhook",
            json={
                "header": {
                    "event_type": "unknown.event"
                },
                "event": {
                    "data": "test"
                }
            },
            content_type="application/json"
        )
        assert response.status_code == 200


class TestCreateWebhookHandler:
    """Tests for the create_webhook_handler factory function."""

    def test_create_with_defaults(self):
        """Test factory function with default endpoint."""
        app = Flask(__name__)
        handler = create_webhook_handler(app)
        assert isinstance(handler, WebhookHandler)
        assert handler.app == app
        assert handler.endpoint == "/webhook"

    def test_create_with_custom_endpoint(self):
        """Test factory function with custom endpoint."""
        app = Flask(__name__)
        handler = create_webhook_handler(app, endpoint="/api/webhook")
        assert handler.endpoint == "/api/webhook"


class TestAsyncHandlers:
    """Tests for async handler support."""

    @pytest.fixture
    def app(self):
        """Create a test Flask app."""
        app = Flask(__name__)
        app.config["TESTING"] = True
        return app

    @pytest.fixture
    def handler(self, app):
        """Create a webhook handler."""
        return WebhookHandler(app)

    def test_register_async_message_handler(self, handler):
        """Test registering an async message handler."""
        @handler.message_handler("text")
        async def async_handler(event):
            return "handled"

        assert "text" in handler.message_handlers

    def test_register_async_event_handler(self, handler):
        """Test registering an async event handler."""
        @handler.event_handler("test.event")
        async def async_handler(event):
            return "handled"

        assert "test.event" in handler.event_handlers
