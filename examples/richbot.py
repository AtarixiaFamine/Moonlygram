"""Send a rich message, the library's headline feature.

    BOT_TOKEN=123:abc python examples/richbot.py

/rich builds one with the RichMessage HTML builder; /blocks sends the same kind
of content as Bot API 10.2 structured blocks.
"""
import os

from moonlygram import RichMessage
from moonlygram.ext import Application, CommandHandler
from moonlygram.rich import (
    InputRichBlockParagraph,
    InputRichBlockPreformatted,
    InputRichBlockSectionHeading,
    bold,
    code,
    link,
)


async def show(update, context):
    msg = (
        RichMessage()
        .heading("Moonlygram")
        .paragraph("A rich message with ", bold("bold"), ", ", code("code"), ", and a ",
                   link("link", "https://example.com"), ".")
        .code_block("await bot.send_rich_message(chat_id, html=msg)", language="python")
        .quote("Built on Bot API 10.2.")
    )
    await context.bot.send_rich_message(update.effective_chat_id, html=msg)


async def show_blocks(update, context):
    blocks = [
        InputRichBlockSectionHeading("Moonlygram", size=2),
        InputRichBlockParagraph("The same idea, described as structured blocks."),
        InputRichBlockPreformatted(
            "await bot.send_rich_message(chat_id, blocks=blocks)", language="python"
        ),
    ]
    await context.bot.send_rich_message(update.effective_chat_id, blocks=blocks)


def main() -> None:
    app = Application.builder().token(os.environ["BOT_TOKEN"]).build()
    app.add_handler(CommandHandler("rich", show))
    app.add_handler(CommandHandler("blocks", show_blocks))
    app.run_polling()


if __name__ == "__main__":
    main()
