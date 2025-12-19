"""Tests for feishu_sdk.event module."""

import pytest
from feishu_sdk.event import Event, InvalidEventException


class TestEvent:
    """Tests for the Event class."""

    def test_valid_event(self):
        """Test creating an event with valid data."""
        data = {
            "header": {
                "event_type": "im.message.receive_v1",
                "event_id": "123456"
            },
            "event": {
                "message": {
                    "message_id": "msg_123",
                    "content": "Hello"
                }
            }
        }
        event = Event(data)
        assert event.header.event_type == "im.message.receive_v1"
        assert event.header.event_id == "123456"
        assert event.event.message.message_id == "msg_123"

    def test_missing_header(self):
        """Test that missing header raises InvalidEventException."""
        data = {
            "event": {"message": "test"}
        }
        with pytest.raises(InvalidEventException) as exc_info:
            Event(data)
        assert "not callback event" in str(exc_info.value)

    def test_missing_event(self):
        """Test that missing event raises InvalidEventException."""
        data = {
            "header": {"event_type": "test"}
        }
        with pytest.raises(InvalidEventException) as exc_info:
            Event(data)
        assert "not callback event" in str(exc_info.value)

    def test_empty_dict(self):
        """Test that empty dict raises InvalidEventException."""
        with pytest.raises(InvalidEventException):
            Event({})

    def test_none_header(self):
        """Test that None header raises InvalidEventException."""
        data = {
            "header": None,
            "event": {"message": "test"}
        }
        with pytest.raises(InvalidEventException):
            Event(data)

    def test_none_event(self):
        """Test that None event raises InvalidEventException."""
        data = {
            "header": {"event_type": "test"},
            "event": None
        }
        with pytest.raises(InvalidEventException):
            Event(data)

    def test_nested_event_data(self):
        """Test event with deeply nested data."""
        data = {
            "header": {
                "event_type": "im.message.receive_v1",
                "tenant_key": "tenant_123"
            },
            "event": {
                "sender": {
                    "sender_id": {
                        "open_id": "ou_123",
                        "user_id": "user_123"
                    },
                    "tenant_key": "tenant_123"
                },
                "message": {
                    "message_id": "msg_123",
                    "message_type": "text",
                    "content": '{"text": "Hello"}'
                }
            }
        }
        event = Event(data)
        assert event.event.sender.sender_id.open_id == "ou_123"
        assert event.event.message.message_type == "text"


class TestInvalidEventException:
    """Tests for InvalidEventException."""

    def test_str_representation(self):
        """Test string representation of exception."""
        exc = InvalidEventException("test error")
        assert str(exc) == "Invalid event: test error"

    def test_repr_representation(self):
        """Test repr is same as str."""
        exc = InvalidEventException("test error")
        assert repr(exc) == str(exc)

    def test_error_info_attribute(self):
        """Test error_info attribute is set."""
        exc = InvalidEventException("my error")
        assert exc.error_info == "my error"
