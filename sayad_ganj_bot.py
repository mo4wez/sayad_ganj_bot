import re
import logging
from database.db_core import WordBook, db
from config import SayadGanjConfig
from asyncio import sleep

from telegram import (
    InlineKeyboardButton,
    Update,
    InlineKeyboardMarkup,
    )
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    )
from constants.messages import (
    TRANSLATE_COMMAND,
    IAM_SORRY,
    FORCE_JOIN_TEXT,
    HELP_MESSAGE,
    )
from constants.keyboards import MARKUP



class SayadGanjBot:
    def __init__(self):
        self.config = SayadGanjConfig()
        self.bot = Application.builder().token(self.config.token).build()
        self.CHECK_JOIN, self.JOIN_CHANNEL = range(2)

    def run(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        
        self.bot.add_handler(
            CommandHandler(
                command='start',
                callback=self.start_message,
            )
        )

        self.bot.add_handler(
            MessageHandler(
                filters=filters.ChatType.PRIVATE & ~filters.COMMAND,
                callback=self.respond_in_private_chat,
            )
        )

        self.bot.add_handler(
            MessageHandler(
                filters=filters.ChatType.GROUPS & ~filters.COMMAND,
                callback=self.respond_in_group_chat,
            )
        )

        self.bot.add_handler(
            CommandHandler(
                command='help',
                callback=self.help,
            )
        )

        self.bot.run_polling()

    async def start_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logging.info('in start message')
        user_id = update.effective_chat.id

        await context.bot.send_message(
            chat_id=user_id,
            text=FORCE_JOIN_TEXT,
            reply_markup=MARKUP,
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(HELP_MESSAGE)

    async def translate(self, update: Update, context: ContextTypes.DEFAULT_TYPE, word_to_trans):
        self.results = WordBook.select().where(
            WordBook.langFullWord == word_to_trans
            )
        logging.info(f'records: {len(self.results)}')

        if self.results:
            reply_text = ''
            for result in self.results:
                cleaned_translation = self.remove_h_tags(result.entry)
                
                if len(self.results) > 1:
                    reply_text += cleaned_translation + '\n'
                    await sleep(0.3)
                else:
                    reply_text += cleaned_translation

            await update.message.reply_text(
                text=reply_text,
                reply_markup=MARKUP,
            )
        else:
            reply_text=IAM_SORRY

            await update.message.reply_text(
                text=reply_text,
            )

        db.close()

    async def respond_in_private_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        word = update.message.text
        await self.translate(update, context, word_to_trans=word)

    async def respond_in_group_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message.text
        if message.startswith(TRANSLATE_COMMAND):
            word = message.split()[1]
            await self.translate(update, context, word_to_trans=word)

    def remove_h_tags(self, word):
        new_word = re.sub(r'<h1>.*?</h1>', '', word)
        return new_word
