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
text references a file through a `tg://photo?id=`, `tg://video?id=`, or
`tg://audio?id=` link, supply those files with `media`, a list of
`InputRichMessageMedia`.

## Streaming

`send_rich_message_draft` updates an ephemeral draft repeatedly (about a 30s
TTL); send the final version with `send_rich_message`. In a blocks draft,
`InputRichBlockThinking` renders a "thinking" placeholder for content that has
not arrived yet; it is valid only in drafts.

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
