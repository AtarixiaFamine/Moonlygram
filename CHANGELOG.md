# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-11-10

Bot API 10.4, complete on the surface the library covers. Widgets are the
release: a block of HTML the app renders inside a message bubble, which, unlike
a rich message, runs as HTML and can call back to the bot. They are modelled end
to end, queries and shared widgets included.

Telegram restricts them for now. Production accepts a widget in private chats
only, a sent widget always has protected content so it cannot be forwarded, and
inline results can describe one but inline mode does not serve them yet. The
library models all of it anyway, because the restriction is Telegram's to lift
and nothing about it is visible in the spec.

The other change reaches existing bots: a callback query now identifies the
recipient of an ephemeral message on its own, so a bot can answer a button press
privately in a chat it holds no user id for.

This release also carries a fix that predates 10.4. Types the caller
constructs are hand-written, and unlike the received types they carry no `raw`
dict. With `slots=True` there is nowhere to put a value the
dataclass does not declare, so an unmodelled field is not merely undocumented,
it is unreachable. `InputMediaVideo` declared six of the spec's thirteen, which
meant no video sent as an `InputMedia` object could carry
`supports_streaming`: Telegram served it as a plain download and the reader
waited for the whole file before playback started. `send_video` took the flag
as a keyword all along, so only the object path was affected, which is why it
survived a release.

The gap is closed across every sent type, not just the media ones, and the
per-family CI checks give way to a scan that finds them.

### Added
- **Widgets.** `send_widget` takes the HTML, `width` / `height` in logical
  pixels, and the two data fields: `public_data`, which is the same everywhere
  the widget appears, and `chat_data`, which belongs to the one message. The
  sent `Message.widget` reports both back. `allow_queries` lets the widget call
  the bot; `is_shared` gives it an id.
- **Widget queries.** A widget's call arrives as a `widget_query` update
  (`WidgetQuery`), dispatched by `WidgetQueryHandler`, which filters on the
  query's data with `pattern` the way `CallbackQueryHandler` does. Answer it
  with `query.answer(data)` or `Bot.answer_widget_query` within 15 seconds; an
  answer reaches only the widget that asked and changes nothing it stores.
  `query.edit_widget_data(...)` changes what everyone sees, finding the message
  whether it sits in a chat or an inline message, and
  `Bot.edit_message_widget_data` is the unbound form.
- `WidgetQueryType` covers the three shapes a query takes, generated as one flat
  type the way `ChatMember` is: bot data plus the sender's TON wallet card
  (`data`), data their wallet signed (`sign_data`), or a transaction they sent
  (`sent_transaction`).
- **Shared widgets.** `send_shared_widget` puts a widget created with
  `is_shared=True` in another message, and `edit_shared_widget_data` changes the
  public data of every copy at once, with a `cache_time` of 5-3600 seconds. A
  query from a forwarded copy arrives as a `shared_widget_query` update
  (`SharedWidgetQuery`, dispatched by `SharedWidgetQueryHandler`), which names
  no chat or message: `widget_id` is all there is to go on.
- `InputWidgetMessageContent` and `InputSharedWidgetMessageContent`, for
  describing a widget as an inline query result.
- **TON wallet objects:** `TonWalletCard` with its `TonWalletCardSticker`,
  `TonNft`, and `TonNftAttribute`, plus `WidgetQueryWallet` for the wallet a
  query carries. Amounts stay strings, in the currency's smallest units, since
  they do not survive a float.
- `Message.ton_wallet_transfer` (`TonWalletTransfer`, with a negative `amount`
  for an outgoing transfer) and `Message.paid_messages_waived`
  (`PaidMessagesWaived`, which holds no fields, so its presence is the whole
  signal).
- **Answering a button press privately, anywhere.** `EphemeralMessageParameters`
  now accepts a `callback_query_id` on its own, and `chat_id` became optional on
  the fourteen send methods that take ephemeral parameters, so passing `None`
  sends the reply to whoever pressed the button. This works in every chat but a
  channel's direct-messages chat, and it is what lets a bot reply privately
  where it has no user id to name.
- `ReplyParameters.quote_rich_texts`, for quoting a run of a rich message. A
  string plus offsets cannot express the structure a rich run carries, so the
  nodes go across as themselves; an incoming quote arrives the same way in
  `TextQuote.rich_texts`. A received `RichTextNode` can go straight back.
- `get_chat_share_theme_backdrops`, with `ChatShareTheme`, `ChatShareThemeEmoji`
  and `ChatShareThemeUniqueGift` merged into one flat type, plus
  `ChatShareThemeBackdrop`, `ChatShareThemeBackdrops`, and `EmojiType`.
  `ChatFullInfo.share_theme` and `ChatFullInfo.ton_wallet_card` reach them,
  though `ChatFullInfo` itself stays an unmodelled dict.
- `RichTextNode` parses 10.4's `ton_address` run. Like a bank card number it is
  detected by Telegram rather than authored, so it only had to parse on the way
  in; the `ton_address` and `bank_card_number` entity types need no code, since
  an entity type is a plain string here.
- A `widget_query` or `shared_widget_query` update now fills
  `Update.effective_user_id`, and a `widget_query` from a chat fills
  `Update.effective_chat_id`.
- `AreaPosition`, which 10.4 renamed from `StoryAreaPosition` now that a wallet
  card positions stickers the same way a story does. Stories are not modelled,
  so nothing referred to the old name.
- `InputMediaVideo.supports_streaming`, plus `thumbnail`, `cover`,
  `start_timestamp`, `caption_entities`, `show_caption_above_media`, and
  `has_spoiler`.
- `InputMediaPhoto.caption_entities`, `show_caption_above_media`, and
  `has_spoiler`; `InputMediaAnimation.thumbnail`, `caption_entities`,
  `show_caption_above_media`, and `has_spoiler`; `InputMediaAudio.thumbnail`
  and `caption_entities`; `InputMediaDocument.thumbnail`, `caption_entities`,
  and `disable_content_type_detection`; `InputMediaVoiceNote.caption_entities`.
- `InputMediaLivePhoto`, which `sendMediaGroup` has accepted since Bot API 10.1
  and the library did not model at all. It carries the video as `media` and the
  still frame as `photo`; both upload.
- `Chat.first_name`, `last_name`, `is_forum`, and `is_direct_messages`. The
  first two are the only name a private chat has, so a private `Chat` was
  reaching handlers anonymous.
- `User.is_premium` and `added_to_attachment_menu`, plus the ten `get_me`
  capability flags (`can_join_groups`, `supports_inline_queries`,
  `can_connect_to_business`, `has_main_web_app`, and the rest).
- `ChatPermissions.can_react_to_messages` and `can_edit_tag`, so
  `set_chat_permissions` can no longer silently omit them.
- `ReplyParameters.checklist_task_id` and `poll_option_id`.
- `InputTextMessageContent.entities` and `link_preview_options`.
- The missing inline-result fields: `caption_entities` and
  `show_caption_above_media` across the photo, video, document, and cached
  variants; `photo_width` / `photo_height`; `video_width` / `video_height` /
  `video_duration`; and `thumbnail_width` / `thumbnail_height` on
  `InlineQueryResultArticle` and `InlineQueryResultDocument`.

A nested `thumbnail`, `cover`, or live-photo `photo` accepts an `InputFile` and
uploads as its own multipart part, like `media` already did.

### Changed
- `EphemeralMessageParameters.receiver_user_id` is optional, and constructing
  the type with neither it nor a `callback_query_id` raises `ValueError`.
  Naming nobody is not a neutral default: Telegram reads such a message as an
  ordinary one and shows it to the whole chat, which is the mistake this type
  exists to prevent. Every existing call is unaffected.
- `chat_id` is typed `Optional` on `send_message`, `send_rich_message`,
  `send_photo`, `send_live_photo`, `send_document`, `send_audio`, `send_video`,
  `send_animation`, `send_voice`, `send_video_note`, `send_sticker`,
  `send_location`, `send_contact`, and `send_venue`. It stays positional with no
  default, so passing it is still required and no existing call changes; `None`
  is how the ephemeral-reply case is spelled.
- The vendored spec moved from 10.3 to 10.4 (425 types, 193 methods), and the
  generator now owns 80 types.
- The spec drift check no longer takes a hand-maintained list of type names.
  Listing them is what failed: the keyboards were added to the check in 1.3.1
  and the media types were not, so they kept drifting. CI now finds every
  dataclass the spec names that carries a `to_dict` and no `raw`, and holds all
  71 of them to the spec. It also sets every modelled field and reads the
  payload back, since declaring a field and serializing it are separate
  mistakes.

### Notes
- `getUniqueGift` and `deleteBusinessAccountGift`, recorded in the method
  coverage test's `UNIMPLEMENTED` list alongside the rest of the gift and
  business-account surface. `bot.call()` reaches both in the meantime.
- `verifyUser` and `verifyChat` gained `custom_description_parse_mode` and
  `custom_description_entities`; both methods were already deferred, so there
  was nothing to change.

## [1.3.1] - 2026-08-26

The keyboard types are hand-written, while everything around them is generated
and drift-checked against the spec. They fell behind: `copy_text` had been in
the Bot API since 7.11 and was unreachable, and a `slots=True` dataclass gives
no way to work around a missing field. They are now checked against the spec
too, so the whole family fails CI the next time it drifts.

### Added
- `CopyTextButton` and `InlineKeyboardButton.copy_text`: a button that copies
  text to the clipboard. Also `web_app`, `login_url`, `switch_inline_query`,
  `switch_inline_query_current_chat`, `switch_inline_query_chosen_chat`,
  `callback_game`, and `pay`, completing the type against the spec.
- `KeyboardButton.request_contact`, `request_location`, `request_users`,
  `request_chat`, `request_managed_bot`, `request_poll`, and `web_app`;
  `ReplyKeyboardMarkup.is_persistent`, `input_field_placeholder`, and
  `selective`.
- `Message.reply_markup`, parsed as an `InlineKeyboardMarkup`. A message's
  keyboard was reachable only as `message.raw["reply_markup"]`, so an edit that
  rebuilt it from typed objects dropped whatever the button type did not model.
  Telegram clears the keyboard on any edit that omits `reply_markup`, so that
  loss was silent and permanent.
- `InlineKeyboardButton.from_dict` and `InlineKeyboardMarkup.from_dict`, so a
  received keyboard round-trips back out unchanged.

### Fixed
- Arbitrary callback data no longer strips a button while tokenising it.
  `CallbackDataCache.process_keyboard` rebuilt each button from `text`,
  `callback_data`, and `url` alone, dropping `style`, `icon_custom_emoji_id`,
  `disabled`, and the markup's `force_reply`. It now copies the button and
  replaces one field, so new fields carry through on their own.

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
