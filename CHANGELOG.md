# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-12-19

### Added
- Initial release of Feishu Bot SDK
- `MessageApiClient` for sending messages via Feishu/Lark API
  - Text message support
  - Interactive card support
  - Message card updates
  - Tenant access token management
- `WebhookHandler` for handling incoming Feishu webhooks
  - URL verification handling
  - Message handler decorators
  - Event handler decorators
  - Async handler support
  - Flask integration
- `Event` class for parsing webhook events
- Utility functions for dictionary-to-object conversion
- Environment variable configuration support

[Unreleased]: https://github.com/liannejl/feishu-bot-sdk/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/liannejl/feishu-bot-sdk/releases/tag/v0.1.0
