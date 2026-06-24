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
    .paragraph("Shipped ", bold("rich messages"), " — see ", link("the docs", "https://example.com"))
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

## Streaming

`send_rich_message_draft` updates an ephemeral draft repeatedly (about a 30s
TTL); send the final version with `send_rich_message`.

See the [rich API reference](api/rich.md) for every block and inline helper.
