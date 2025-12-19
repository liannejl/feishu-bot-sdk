# Feishu Bot SDK

[![PyPI version](https://badge.fury.io/py/feishu-bot-sdk.svg)](https://badge.fury.io/py/feishu-bot-sdk)
[![Python Versions](https://img.shields.io/pypi/pyversions/feishu-bot-sdk.svg)](https://pypi.org/project/feishu-bot-sdk/)
[![Tests](https://github.com/liannejl/feishu-bot-sdk/actions/workflows/test.yml/badge.svg)](https://github.com/liannejl/feishu-bot-sdk/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple Python SDK for building Feishu/Lark bots with messaging and webhook capabilities.

Built and maintained by [Month2Month](https://month2month.com).

## Features

- **Message API Client**: Send text messages, interactive cards, and update existing cards
- **Webhook Handler**: Handle incoming Feishu webhook events with Flask integration
- **Event Processing**: Parse and process Feishu events with type-safe object access
- **Async Support**: Support for both sync and async message handlers
- **Environment Configuration**: Easy setup via environment variables

## Installation

```bash
pip install feishu-bot-sdk
```

For development:
```bash
pip install -e ".[dev]"
```

## Quick Start

### Sending Messages

```python
from feishu_sdk import MessageApiClient

# Initialize with credentials
client = MessageApiClient(
    app_id="your_app_id",
    app_secret="your_app_secret",
    lark_host="https://open.feishu.cn"
)

# Or initialize from environment variables (APP_ID, APP_SECRET)
client = MessageApiClient.from_env("https://open.feishu.cn")

# Send a text message
client.send_text_with_open_id("user_open_id", "Hello World!")

# Send an interactive card
card_content = '''
{
    "config": {"wide_screen_mode": true},
    "elements": [
        {"tag": "div", "text": {"content": "Hello Card!", "tag": "lark_md"}}
    ]
}
'''
message_id = client.send_card_with_open_id("user_open_id", card_content)

# Update a card
client.send_update_message_card(message_id, updated_card_content)
```

### Handling Webhooks

```python
from flask import Flask
from feishu_sdk import WebhookHandler, create_webhook_handler

app = Flask(__name__)
webhook = WebhookHandler(app)

# Handle text messages
@webhook.message_handler("text")
def handle_text(event):
    message = event.event.message
    print(f"Received: {message.content}")

# Handle specific event types
@webhook.event_handler("im.chat.member.user.added_v1")
def handle_user_added(event):
    print(f"User added to chat")

# Async handlers are also supported
@webhook.message_handler("image")
async def handle_image(event):
    await process_image(event)

if __name__ == "__main__":
    app.run(port=3000)
```

### Working with Events

```python
from feishu_sdk import Event, InvalidEventException

try:
    event = Event(request_data)

    # Access event data with dot notation
    event_type = event.header.event_type
    sender_id = event.event.sender.sender_id.open_id
    message_content = event.event.message.content

except InvalidEventException as e:
    print(f"Invalid event: {e}")
```

## Configuration

### Environment Variables

The SDK supports configuration via environment variables:

| Variable | Description |
|----------|-------------|
| `APP_ID` | Your Feishu app ID |
| `APP_SECRET` | Your Feishu app secret |

You can also use custom environment variable names:

```python
client = MessageApiClient.from_env(
    "https://open.feishu.cn",
    app_id_env="MY_FEISHU_APP_ID",
    app_secret_env="MY_FEISHU_APP_SECRET"
)
```

## API Reference

### MessageApiClient

| Method | Description |
|--------|-------------|
| `send_text_with_open_id(open_id, content)` | Send text message to user |
| `send_card_with_open_id(open_id, content)` | Send interactive card to user |
| `send_update_message_card(message_id, content)` | Update existing card message |
| `send(receive_id_type, receive_id, msg_type, content)` | Generic send method |

### WebhookHandler

| Method | Description |
|--------|-------------|
| `message_handler(message_type)` | Decorator to register message handlers |
| `event_handler(event_type)` | Decorator to register event handlers |
| `init_app(app)` | Initialize with Flask app |

## Development

### Setup

```bash
git clone https://github.com/liannejl/feishu-bot-sdk.git
cd feishu-bot-sdk
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
pytest --cov=feishu_sdk  # with coverage
```

### Code Quality

```bash
black feishu_sdk tests    # format code
isort feishu_sdk tests    # sort imports
mypy feishu_sdk           # type checking
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [Feishu Open Platform Documentation](https://open.feishu.cn/document/)
- [GitHub Repository](https://github.com/liannejl/feishu-bot-sdk)
- [Issue Tracker](https://github.com/liannejl/feishu-bot-sdk/issues)
- [Changelog](CHANGELOG.md)
