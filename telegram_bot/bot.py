import logging
import os

from telegram import Update, MessageEntity
from telegram.constants import MessageEntityType
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

from telegram_bot.tagesschau_feed import TagesschauFeedReader, News

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            'Das ist ein Bot, der nur die wichtigsten Nachrichten aus dem '
            'Taggeschau-RSS-Kanal herauszieht und anzeigt.'
        )
    )


def update_news_store(news_list: list[News]):
    pass


def filter_news(news_list: list[News]):
    return news_list


async def fetch_important_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    news_list = TagesschauFeedReader().get_news()
    news_list_filtered = filter_news(news_list)

    for news in news_list_filtered:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=str(news),
        )

    update_news_store(news_list)


if __name__ == '__main__':
    api_key = os.environ.get('TAGESSCHAU_BOT_API_KEY')
    if api_key is None:
        logging.critical('API key not set, running the bot failed!')

    application = ApplicationBuilder().token(api_key).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    fetch_handler = CommandHandler('news', fetch_important_news)
    application.add_handler(fetch_handler)

    application.run_polling()
