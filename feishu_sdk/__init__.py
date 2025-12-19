"""
Feishu/Lark Bot SDK

A simple Python SDK for building Feishu/Lark bots with messaging capabilities.
"""

from .api import LarkException, MessageApiClient
from .event import Event, InvalidEventException
from .utils import dict_2_obj
from .webhook import WebhookHandler, create_webhook_handler

__version__ = "0.1.0"
__all__ = [
    "MessageApiClient",
    "LarkException",
    "Event",
    "InvalidEventException",
    "dict_2_obj",
    "WebhookHandler",
    "create_webhook_handler",
]
