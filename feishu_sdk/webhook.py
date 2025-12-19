import asyncio
import json
from threading import Thread
from typing import Any, Callable, Dict, Optional

from flask import Flask, jsonify, request

from .event import Event, InvalidEventException


class WebhookHandler:
    """
    Handles Feishu webhook events with standard URL verification and message processing
    """

    def __init__(self, app: Optional[Flask] = None, endpoint: str = "/webhook"):
        self.app = app
        self.endpoint = endpoint
        self.message_handlers = {}
        self.event_handlers = {}

        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        """Initialize the webhook handler with a Flask app"""
        self.app = app
        app.add_url_rule(self.endpoint, "feishu_webhook", self._webhook_handler, methods=["POST"])

    def message_handler(self, message_type: str = "text"):
        """Decorator to register message handlers"""

        def decorator(func: Callable):
            self.message_handlers[message_type] = func
            return func

        return decorator

    def event_handler(self, event_type: str):
        """Decorator to register event handlers"""

        def decorator(func: Callable):
            self.event_handlers[event_type] = func
            return func

        return decorator

    def _webhook_handler(self):
        """Main webhook handler that processes Feishu events"""
        req_data = request.json

        # Handle URL verification
        if "type" in req_data and req_data["type"] == "url_verification":
            return jsonify({"challenge": req_data["challenge"]})

        # Handle events
        try:
            event = Event(req_data)
            event_type = event.header.event_type

            # Handle message events
            if event_type == "im.message.receive_v1":
                thread = Thread(target=self._async_message_processing, args=(req_data,))
                thread.start()
                return jsonify()

            # Handle other events
            elif event_type in self.event_handlers:
                thread = Thread(target=self._async_event_processing, args=(event_type, req_data))
                thread.start()
                return jsonify()

            return jsonify()

        except InvalidEventException:
            return jsonify({"error": "Invalid event"}), 400

    def _async_message_processing(self, req_data: Dict[str, Any]):
        """Process message events asynchronously"""
        asyncio.run(self._process_message(req_data))

    def _async_event_processing(self, event_type: str, req_data: Dict[str, Any]):
        """Process non-message events asynchronously"""
        asyncio.run(self._process_event(event_type, req_data))

    async def _process_message(self, req_data: Dict[str, Any]):
        """Process incoming messages"""
        try:
            event = Event(req_data)
            message = event.event.message
            message_type = message.message_type

            if message_type in self.message_handlers:
                handler = self.message_handlers[message_type]
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)

        except Exception as e:
            print(f"Error processing message: {e}")

    async def _process_event(self, event_type: str, req_data: Dict[str, Any]):
        """Process non-message events"""
        try:
            event = Event(req_data)
            handler = self.event_handlers[event_type]

            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)

        except Exception as e:
            print(f"Error processing event {event_type}: {e}")


def create_webhook_handler(app: Flask, endpoint: str = "/webhook") -> WebhookHandler:
    """Factory function to create and configure a webhook handler"""
    return WebhookHandler(app, endpoint)
