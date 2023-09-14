from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    )
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    InlineQueryHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    )
from config import SayadGanjConfig


class SayadGanjBot:
    def __init__(self):
        self.config = SayadGanjConfig()
        self.bot = Application.builder().token(self.config.token).build()

        print('init')


    def run(self):
        self.bot.add_handler(
            CommandHandler(
                command='start',
                callback=self.start,
                filters=filters.TEXT,
            )
        )

        self.bot.run_polling()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Hello there!"
        )