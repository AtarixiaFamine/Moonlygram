# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Button styling from Bot API 9.4: `style` ("primary", "success", or "danger")
  and `icon_custom_emoji_id` on both `InlineKeyboardButton` and `KeyboardButton`.
  `style` is typed as a `Literal` so unknown values are caught at type-check time.
- `User.language_code` (the user's IETF language tag) is now parsed.
- Payments: `send_invoice`, `create_invoice_link`, `answer_shipping_query`, and
  `answer_pre_checkout_query` methods; the `shipping_query` and
  `pre_checkout_query` updates with `ShippingQueryHandler` /
  `PreCheckoutQueryHandler` and `.answer()` shortcuts on the query objects.
  New types `LabeledPrice`, `ShippingOption`, `Invoice`, `SuccessfulPayment`,
  `RefundedPayment`, `OrderInfo`, `ShippingAddress`, and `Message.invoice` /
  `successful_payment` / `refunded_payment` parsing.
- Telegram Stars: `get_star_transactions`, `get_my_star_balance`,
  `refund_star_payment`, and `edit_user_star_subscription` methods, with the
  `StarTransactions`, `StarTransaction`, `StarAmount`, `AffiliateInfo`,
  `TransactionPartner`, and `RevenueWithdrawalState` types.

### Fixed
- `markdown_to_rich`: a literal `<br>` inside a Markdown table cell (the GitHub
  idiom for an in-cell line break) now becomes a real break instead of showing
  as literal text.

## [0.1.1]

### Fixed
- `markdown_to_rich`: inline formatting inside table cells now renders. Bold,
  italics, links, and math in a cell were previously shown as literal Markdown
  because cells were escaped and stashed before the inline passes ran. Cells are
  now run through the inline pipeline, and the split into cells happens before
  the math and emphasis passes, so a `$...$` span can no longer swallow a column
  delimiter and fuse two cells.

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
