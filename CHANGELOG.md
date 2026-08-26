# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-08-26

Bot API 10.3, complete: every line of the changelog is implemented. The vendored
spec moved from 10.1 to 10.3, so the 10.2 surface that was hand-written against
the changelog is now generated and drift-checked, the domains held back for it
are modelled, rich messages are typed in both directions for the first time, and
a file can finally be uploaded from inside a media object.

### Added
- Rich message buttons (Bot API 10.3): `InputRichBlockButtons` puts a row of
  1-8 `RichMessageButton` in the message body, with `align` and a `style` of
  "primary", "success", "danger", or "link".
- `InputRichBlockDocument` (a block holding a general file) and
  `InputRichBlockExpandableBlockQuotation` (a quotation the reader can expand
  and collapse). Rich message text can reference an uploaded file with a
  `tg://document?id=` link.
- `is_compact` on `InputRichBlockTable`, for cells with smaller indents.
- `DisabledButton` and `InlineKeyboardButton.disabled`, which shows a button
  that does nothing; `force_reply` on `InlineKeyboardMarkup` and
  `ReplyKeyboardMarkup`.
- `can_stop` and `keep_on_stop` on `send_rich_message_draft`, offering the
  reader a control that stops a streaming generation. Stopping produces a
  `stopped_message_generation` update (`MessageGenerationStopped`), dispatched
  by the new `MessageGenerationStoppedHandler`.
- `can_send_welcome_messages` on `promote_chat_member`,
  `ChatAdministratorRights`, and `ChatMemberAdministrator`.
- `edit_ephemeral_rich_message_text`, replacing an ephemeral message's text
  with rich content, alongside the parameters `editEphemeralMessage*` was
  missing: `entities` and `link_preview_options` on the text edit,
  `caption_entities` and `show_caption_above_media` on the caption edit.
  `InputMediaDocument` joins the media a rich message can reference, for the
  new `tg://document?id=` links.
- Communities (Bot API 10.2, deferred until the spec caught up): the
  `Community` type and the `community_chat_added`, `community_chat_joined`, and
  `community_chat_removed` service messages on `Message`.
- `BotSubscriptionUpdated` and `Update.subscription`, dispatched by the new
  `BotSubscriptionHandler`.
- **Received rich messages.** `Message.rich_message` now parses into
  `RichMessageContent`, with every `RichBlock` and `RichText` variant modelled:
  the two abstract unions are generated as flat types the same way `ChatMember`
  is, so a received message's headings, tables, media, quotations, and buttons
  are all typed. Rich text arrives as a plain string, a list, or a
  `RichTextNode`, whichever the payload holds.
- `UniqueGiftInfo` (with `UniqueGift` and its model, symbol, backdrop, and
  colors) is modelled and reachable from `Message.unique_gift`, carrying 10.3's
  `text`, `entities`, and `is_private`. The gift *methods* stay unimplemented.
- `send_message_draft`, the plain-text counterpart to `send_rich_message_draft`,
  with the same `can_stop` and `keep_on_stop` controls.
- `send_live_photo` and the `LivePhoto` type on `Message.live_photo`. The method
  was unimplemented, which was the last thing keeping 10.3's ephemeral swap from
  covering every send method the changelog names.
- **Uploading a new file inside a media object.** Every `InputMedia` takes an
  `InputFile` for `media` (as does `InputSticker` for `sticker`), and `Session`
  hoists it into its own multipart part referenced by an `attach://` name. This
  is what 10.3 added to `editEphemeralMessageMedia`, and it lands everywhere the
  same shape appears: `send_media_group`, `edit_message_media`, the sticker
  methods, and a rich message's media and document blocks, none of which could
  upload before.
- The hand-written rich blocks are now checked against the vendored spec, the
  same way the generated types are. The spec did not model them before 10.3.

### Fixed
- CI linted against ruff's default rule set, which widens between releases:
  ruff 0.16 folded pyupgrade, isort and more into its defaults, failing the
  build on unchanged code (the released 0.4.0 reports 1344 errors under it).
  The rule set is now pinned in `pyproject.toml`, so upgrading the linter no
  longer changes what the project enforces.

### Removed
- The `receiver_user_id` and `callback_query_id` parameters, replaced by
  `ephemeral_message_parameters` (see below).

### Changed
- **Ephemeral recipients moved into an object.** Bot API 10.3 replaced the
  `receiver_user_id` and `callback_query_id` parameters with a single
  `ephemeral_message_parameters`, taking the new `EphemeralMessageParameters`
  type; it also adds `replace_callback_query_message`, which shows the
  ephemeral message in place of the one the button was attached to.
  `send_rich_message` gains the parameter as well.

  **This is a breaking change.** Code passing the old pair now raises
  `TypeError`. Wrap the two values in an `EphemeralMessageParameters` and pass
  them as `ephemeral_message_parameters`; see the ephemeral messages guide for
  a before-and-after. The hard failure is deliberate — Telegram stopped reading
  the old parameters, so silently accepting them would have sent the message
  publicly instead of to one user.
- `RichBlockCaption`, `RichBlockTableCell`, and `RichMessageButton` moved from
  `moonlygram.rich.blocks` to `moonlygram.types` and gained a `from_dict`, since
  the Bot API uses one type for both directions. They are still importable from
  `moonlygram.rich`, so no import breaks.
- The spec's received `RichMessage` and `RichText` are exposed as
  `RichMessageContent` and `RichTextNode`: both spec names are already taken by
  the send-side API (the `RichMessage` builder and the loose `RichText` alias),
  which keep their meaning unchanged.

## [0.4.0] - 2026-07-21

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
  until the vendored spec is refreshed to 10.2. (Both land in 0.5.0.)

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
