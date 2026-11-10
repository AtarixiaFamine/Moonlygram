# Rich messages

Bot API 10.1 added rich messages: block-level structure (headings, paragraphs,
code blocks, tables, collapsibles, math) that plain messages cannot express.
`send_rich_message` is one more `Bot` method; build its content with
`RichMessage` plus the inline helpers in `moonlygram.rich`.

```python
from moonlygram import RichMessage
from moonlygram.rich import bold, link

msg = (
    RichMessage()
    .heading("Release notes")
    .paragraph("Shipped ", bold("rich messages"), ", see ", link("the docs", "https://example.com"))
    .code_block("pip install -U moonlygram", language="bash")
)

await bot.send_rich_message(chat_id, html=msg)
```

Everything is HTML-escaped as it is added, so plain strings are always safe to
pass; use `raw()` for an HTML fragment you have built yourself.

## From Markdown

`markdown_to_rich` converts an existing Markdown string to rich-message HTML:

```python
from moonlygram import markdown_to_rich

await bot.send_rich_message(chat_id, html=markdown_to_rich("# Hi\n\nSome **bold** text."))
```

## Structured blocks

Bot API 10.2 adds a third content form. Instead of an HTML or Markdown string,
describe the message as a list of block objects and pass them as `blocks`. The
block types live in `moonlygram.rich`.

```python
from moonlygram.rich import (
    InputRichBlockList,
    InputRichBlockListItem,
    InputRichBlockParagraph,
    InputRichBlockSectionHeading,
)

await bot.send_rich_message(
    chat_id,
    blocks=[
        InputRichBlockSectionHeading("Release notes", size=1),
        InputRichBlockParagraph("Two things shipped:"),
        InputRichBlockList(
            items=[
                InputRichBlockListItem(blocks=[InputRichBlockParagraph("Structured blocks")]),
                InputRichBlockListItem(blocks=[InputRichBlockParagraph("Ephemeral messages")]),
            ]
        ),
    ],
)
```

Pass exactly one of `html`, `markdown`, or `blocks`. When `html` or `markdown`
text references a file through a `tg://photo?id=`, `tg://video?id=`,
`tg://audio?id=`, or `tg://document?id=` link, supply those files with `media`,
a list of `InputRichMessageMedia`. Each entry takes an `InputFile` to upload a
new file, or a `file_id` / URL string.

### Media

`InputRichBlockPhoto`, `InputRichBlockVideo`, `InputRichBlockAnimation`,
`InputRichBlockAudio`, `InputRichBlockVoiceNote`, and `InputRichBlockDocument`
each wrap the matching `InputMedia` type. The wrapped media's own `caption` is
ignored; the block's `caption` is what the reader sees.

Set `supports_streaming` on a video you upload. Without it Telegram serves the
file as a plain download and the reader waits for the whole thing before
playback starts. It applies to uploads only: a `file_id` keeps whatever the
original upload was sent with.

```python
from moonlygram import InputFile, InputMediaVideo
from moonlygram.rich import InputRichBlockVideo, RichBlockCaption

InputRichBlockVideo(
    InputMediaVideo(
        InputFile("clip.mp4"),
        thumbnail=InputFile("thumb.jpg"),
        width=1920,
        height=1080,
        duration=42,
        supports_streaming=True,
    ),
    caption=RichBlockCaption(text="The finished render"),
)
```

`cover` sets the frame shown before playback starts, and `start_timestamp` the
second the video opens at. Nested files upload as their own multipart parts, so
the video and its thumbnail can both be `InputFile`s.

!!! warning "Keep video in a rich message under about 10 MB"

    Tapping a larger video in a rich message plays a black frame. Measured on
    2026-08-28 against live Telegram with lossless trims of one 1080p60 H.264
    source: 5.2 MB plays, 13.5 MB and above do not. It affects both ways a
    rich message carries media, the video block and the `tg://video?id=`
    reference, so switching between them is not a way around it.

    The same file sent with `send_video` plays normally at 44 MB, and the
    upload itself is intact either way, so this is a rendering fault on
    Telegram's side rather than a limit on what you can send. Until it is
    fixed, send a large video as its own `send_video` message next to the rich
    one.

### Quoting a rich message

A reply normally quotes with `quote` and `quote_entities`, a string plus
offsets. A run of rich text can carry structure that neither expresses, so Bot
API 10.4 gives it `ReplyParameters.quote_rich_texts`, which takes the rich
nodes themselves. An incoming quote arrives the same way, in
`TextQuote.rich_texts`.

```python
from moonlygram import ReplyParameters

await bot.send_message(
    chat_id,
    "About that line:",
    reply_parameters=ReplyParameters(
        message_id=message.message_id,
        quote_rich_texts=[{"type": "bold", "text": "the bold bit"}],
    ),
)
```

A received `RichTextNode` can go straight back, which is how a bot quotes the
exact run it is replying about.

### Buttons

`InputRichBlockButtons` puts a row of 1-8 buttons in the message body. Each
`RichMessageButton` sets exactly one action, and `style` is `"primary"`,
`"success"`, `"danger"`, or `"link"`. A button carrying `DisabledButton()` is
shown but does nothing.

```python
from moonlygram import DisabledButton
from moonlygram.rich import InputRichBlockButtons, RichMessageButton

InputRichBlockButtons(
    [
        RichMessageButton("Read more", url="https://example.com", style="link"),
        RichMessageButton("Subscribe", callback_data="sub", style="primary"),
        RichMessageButton("Sold out", disabled=DisabledButton()),
    ],
    align="center",
)
```

The same `disabled` field works on ordinary keyboards through
`InlineKeyboardButton`, and both `InlineKeyboardMarkup` and
`ReplyKeyboardMarkup` accept `force_reply` to show the reply interface
alongside the keyboard.

## Streaming

`send_rich_message_draft` updates an ephemeral draft repeatedly (about a 30s
TTL); send the final version with `send_rich_message`. In a blocks draft,
`InputRichBlockThinking` renders a "thinking" placeholder for content that has
not arrived yet; it is valid only in drafts.

Drafts reach private chats only. Sending one to a group is rejected with
`TEXTDRAFT_PEER_INVALID`, which the Bot API does not document.

Pass `can_stop=True` to give the reader a control that stops the generation.
Pressing it produces a `stopped_message_generation` update, which
`MessageGenerationStoppedHandler` receives; the update names the draft with
`draft_id`. `keep_on_stop=True` leaves the text written so far in place.

```python
from moonlygram.ext import MessageGenerationStoppedHandler

async def stopped(update, context):
    drafts.cancel(update.stopped_message_generation.draft_id)

app.add_handler(MessageGenerationStoppedHandler(stopped))
```

## Receiving

An incoming rich message arrives on `Message.rich_message` as a
`RichMessageContent`: `is_rtl`, plus `blocks`, a list of `RichBlock`. Each block
names its variant in `type` and carries that variant's fields.

```python
async def on_rich(update, context):
    rich = update.effective_message.rich_message
    if rich is None:
        return
    for block in rich.blocks:
        if block.type == "section_heading":
            print(block.size, block.text)
        elif block.type == "table":
            print(len(block.cells), "rows", "compact" if block.is_compact else "")
```

Rich text is whatever the payload holds: a plain `str`, a list mixing strings
and nodes, or a single `RichTextNode` naming its own `type` ("bold", "code",
"custom_emoji", and so on). The `RichTextValue` alias covers all three.

```python
from moonlygram import RichTextNode

def plain(value) -> str:
    """Flatten received rich text down to its characters."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "".join(plain(v) for v in value)
    return plain(value.text) if isinstance(value, RichTextNode) else ""
```

The spec calls these two types `RichMessage` and `RichText`. Both names are
already taken here by the send side — the builder and the loose input alias —
so the received classes are `RichMessageContent` and `RichTextNode`.

## Editing

`edit_rich_message_text` replaces the text of an already-sent message with
rich content. It takes the same `html` / `markdown` / `blocks` / `media` forms
as `send_rich_message`:

```python
await bot.edit_rich_message_text(
    chat_id=chat_id, message_id=message_id, markdown="All **done**."
)
```

See the [rich API reference](api/rich.md) for every block and inline helper.
