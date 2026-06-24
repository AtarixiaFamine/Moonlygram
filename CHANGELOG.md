# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0]

First public release.

### Added
- Async `Bot` covering the common Bot API surface: messaging and editing,
  media, chat and member management, bot configuration, forum topics, stickers,
  inline mode, and the remaining update types.
- `moonlygram.ext`: `Application` + `ApplicationBuilder`, handler groups,
  filters, `ConversationHandler` (timeouts, nesting, persistence), `JobQueue`,
  rate limiting, arbitrary callback data, and concurrent dispatch.
- Rich messages (Bot API 10.1): the `RichMessage` builder, inline helpers, and
  `markdown_to_rich`.
- A typed error hierarchy, builder lifecycle hooks, a `helpers` module, and
  `ContextTypes`.
- Spec-driven type generation (`codegen/`) producing the received data types
  with full field coverage, guarded by drift tests.
- `py.typed`: the package ships type information and passes `mypy --strict`.
