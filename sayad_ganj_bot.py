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
    CallbackContext,
    filters,
    )
from constants.messages import TRANSLATE_COMMAND, YOU, IAM_SORRY, ASKED
from config import SayadGanjConfig
from database.db_core import WordBook, db
import re


class SayadGanjBot:
    def __init__(self):
        self.config = SayadGanjConfig()
        self.bot = Application.builder().token(self.config.token).build()

        print('init')


    def run(self):

        self.bot.add_handler(
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND,
                callback=self.translate,
            )
        )


        self.bot.add_handler(
            CommandHandler(
                command='start',
                callback=self.start,
                filters=filters.TEXT,
            )
        )

        self.bot.add_handler(
            CallbackQueryHandler(callback=0)
        )

        self.bot.run_polling()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Hello there!"
        )

    async def translate(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message.text

        if message.startswith(TRANSLATE_COMMAND):
            word_for_translate = message.split(' ')[1]

            results = WordBook.select().where(
                WordBook.langFullWord == word_for_translate
                )

            if results:

                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text='Here your result',
                )


                for res in results:
                    translation = res.entry
                    cleaned_translation = re.sub(r'<h1>.*?</h1>', '', translation)

                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=cleaned_translation,
                    )


        db.close()

