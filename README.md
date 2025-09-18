# Feishu Bot SDK

A simple Python SDK for building Feishu/Lark bots with messaging capabilities.

## Installation

```bash
pip install feishu-bot-sdk
```

For local development:
```bash
pip install -e .
```

## Usage

### Basic Setup

```python
from feishu_sdk import MessageApiClient

# Initialize with credentials
client = MessageApiClient(
    app_id="your_app_id",
    app_secret="your_app_secret",
    lark_host="https://open.feishu.cn"
)

# Or initialize from environment variables
client = MessageApiClient.from_env("https://open.feishu.cn")
```

### Sending Messages

```python
# Send text message
client.send_text_with_open_id("user_open_id", "Hello World!")

# Send interactive card
card_content = '{"config":{"wide_screen_mode":true},"elements":[{"tag":"div","text":{"content":"Hello Card!","tag":"lark_md"}}]}'
client.send_card_with_open_id("user_open_id", card_content)
```

### Event Handling

```python
from feishu_sdk import Event, InvalidEventException

try:
    event = Event(request_data)
    # Handle event
    print(f"Event type: {event.header.event_type}")
    print(f"Event data: {event.event}")
except InvalidEventException as e:
    print(f"Invalid event: {e}")
```

## Requirements

- Python 3.7+
- requests
- python-dotenv

## License

MIT