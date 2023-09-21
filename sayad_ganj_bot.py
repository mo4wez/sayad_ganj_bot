import re
import logging
from database.db_core import WordBook, db
from database.user_model import User
from database.user_model import db as user_db
from config import SayadGanjConfig
from asyncio import sleep
from constants.keyboards import GROUP_MARKUP, TAKBAND_MARKUP
from telegram.error import TimedOut
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    )
from constants.messages import (
    TRANSLATE_COMMAND,
    IAM_SORRY,
    FORCE_JOIN_TEXT,
    HELP_MESSAGE,
    )



class SayadGanjBot:
    def __init__(self):
        self.config = SayadGanjConfig()
        self.bot = Application.builder().token(self.config.token).build()

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
        user = update.message.from_user
        chat_id = str(user.id)
        first_name = user.first_name or 'No name'
        username = user.username

        existing_user = User.get_or_none(User.chat_id == chat_id)

        if existing_user:
            existing_user.first_name = first_name
            existing_user.username = username
            existing_user.save()
        else:
            User.create(chat_id=chat_id, first_name=first_name, username=username)

        await context.bot.send_message(
            chat_id=chat_id,
            text=FORCE_JOIN_TEXT,
            reply_markup=TAKBAND_MARKUP,
        )
        
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            text=HELP_MESSAGE,
            reply_markup=GROUP_MARKUP,
            )

    async def translate(self, update: Update, context: ContextTypes.DEFAULT_TYPE, word_to_trans):
        self.results = await self.search_word(word_to_trans)
        if self.results:
            reply_text = ''
            for result in self.results:
                cleaned_translation = self.remove_h_tags(result.entry)
                
                if len(self.results) > 1:
                    reply_text += cleaned_translation + '\n'
                else:
                    reply_text = cleaned_translation

            await update.message.reply_text(
                text=reply_text,
                reply_markup=GROUP_MARKUP,
            )
        else:
            reply_text=IAM_SORRY

            await update.message.reply_text(
                text=reply_text,
            )


    async def respond_in_private_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        word = update.message.text
        await self.translate(update, context, word_to_trans=word)

    async def respond_in_group_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message.text
        if message.startswith(TRANSLATE_COMMAND):
            word = message.split()[1]
            await self.translate(update, context, word_to_trans=word)

    async def search_word(self, word_to_trans):
        try:
            results = WordBook.select().where(
                WordBook.langFullWord == word_to_trans
                )
            await sleep(0.2)
            db.close()
            logging.info(f'records: {len(results)}')

            return results
        
        except TimedOut as e:
            logging.info(f'Exception Error: {e}')

    def remove_h_tags(self, word):
        new_word = re.sub(r'<h1>.*?</h1>', '', word)
        return new_word
