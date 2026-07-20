# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Full parameter coverage for every modelled Bot API method. 266 parameters
  across 39 methods were missing; all are now accepted. The most widely felt:
  `message_thread_id` (forum topics) on every send method, `disable_notification`
  and `protect_content` library-wide, `business_connection_id` on the send and
  edit families, and `entities` / `caption_entities` wherever a caption or text
  is sent.
- Notable per-method gaps closed: `link_preview_options` on `send_message` and
  `edit_message_text`; `duration`, `width`, `height`, `thumbnail`, `cover`,
  `has_spoiler`, and `supports_streaming` on `send_video` (and the matching
  fields on the other media senders); the full modern poll surface on
  `send_poll` (`explanation`, `open_period`, `close_date`, `correct_option_ids`,
  `shuffle_options`, and more); the nine missing administrator rights on
  `promote_chat_member`; and `certificate` / `ip_address` on `set_webhook`.
- New types for the parameters above: `LinkPreviewOptions`,
  `SuggestedPostParameters` (with `SuggestedPostPrice`), `InputPollOption`,
  `ReplyKeyboardRemove`, and `ForceReply`. The last two also join the
  `ReplyMarkup` union, and `InputPollMedia` is a new alias accepting any
  `InputMedia` item as poll media.
- `edit_rich_message_text`, which replaces a message's text with rich content.
  It takes the same `html` / `markdown` / `blocks` / `media` forms as
  `send_rich_message`.
- Generated data types now have a `to_dict`, so an object received from Telegram
  can be passed straight back to a send method (echoing `message.entities`, for
  example).

### Changed
- `send_poll` accepts `InputPollOption` objects as well as plain strings for
  `options`, so an option can carry its own formatting or media. Plain strings
  are normalized to the `InputPollOption` shape on the wire, as the spec
  defines.
- `Session` now serializes nested lists and dicts, so a list of objects works
  anywhere a single object does. This removes the per-call-site conversion that
  `send_media_group`, `set_message_reaction`, `send_invoice`, and
  `create_invoice_link` each did by hand.

### Fixed
- `Defaults(disable_notification=...)` reached only the few methods that
  already exposed the parameter (the forward and copy family,
  `send_media_group`, `pin_chat_message`, `send_invoice`), and
  `Defaults(protect_content=...)` only `send_invoice`. Every send method now
  exposes both, so the defaults apply library-wide as intended.

## [0.3.0] - 2026-07-14

### Added
- Rich messages (Bot API 10.2): structured blocks as a third content form
  alongside HTML and Markdown. `send_rich_message` and `send_rich_message_draft`
  now accept `blocks` (a list of `InputRichBlock*` objects) and `media` (a list
  of `InputRichMessageMedia`). The block types in `moonlygram.rich` cover
  paragraphs, headings, preformatted text, footers, dividers, math, anchors,
  lists, block and pull quotations, collages, slideshows, tables, details, maps,
  and embedded animation, audio, photo, video, and voice-note media, with the
  `RichBlockCaption` and `RichBlockTableCell` helpers. `InputMediaVoiceNote` is
  new.
- Ephemeral messages (Bot API 10.2): `receiver_user_id`, `callback_query_id`,
  and `reply_parameters` on `send_message` and the eleven other affected send
  methods; a new `ReplyParameters` type carrying `ephemeral_message_id`;
  `edit_ephemeral_message_text`, `edit_ephemeral_message_media`,
  `edit_ephemeral_message_caption`, `edit_ephemeral_message_reply_markup`, and
  `delete_ephemeral_message`; `BotCommand.is_ephemeral`; and parsing of
  `Message.receiver_user` and `Message.ephemeral_message_id`.

### Notes
- Communities and the `BotSubscriptionUpdated` update from Bot API 10.2 are not
  modelled yet. Their data stays available on `Message.raw` and `Update.raw`
  until the vendored spec is refreshed to 10.2.

## [0.2.0] - 2026-07-08

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
