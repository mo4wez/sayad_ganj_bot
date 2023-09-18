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
    WELCOME_TEXT,
    TRANSLATE_COMMAND,
    IAM_SORRY,
    CHANNEL_USERNAME,
    USER_STATUS,
    FORCE_JOIN_TEXT,
    JOINED,
    JOIN_SUCCESS,
    JOIN_FAILED,
    HELP_MESSAGE,
    )
from constants.keyboards import (
    FORCE_JOIN_KEYBOARD,
    ADD_TO_GROUP_KEYBOARD,
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
                callback=self.start,
                filters=filters.COMMAND,
            )
        )

        self.bot.add_handler(
            MessageHandler(
                filters=filters.ChatType.PRIVATE,
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
            CallbackQueryHandler(callback=self.is_user_joined)
        )

        self.bot.add_handler(
            CommandHandler(
                command='help',
                callback=self.help,
            )
        )

        self.bot.run_polling()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logging.info('in start')
        user_id = update.effective_chat.id
        user_status = await context.bot.get_chat_member(
            chat_id=CHANNEL_USERNAME,
            user_id=user_id,
        )

        if user_status.status not in USER_STATUS:
            markup = InlineKeyboardMarkup(FORCE_JOIN_KEYBOARD)
            await context.bot.send_message(
                chat_id=user_id,
                text=FORCE_JOIN_TEXT,
                reply_markup=markup,
            )
        
        else:
            markup = InlineKeyboardMarkup(ADD_TO_GROUP_KEYBOARD)
            await context.bot.send_message(
                chat_id=user_id,
                text=WELCOME_TEXT,
                reply_markup=markup
            )

        return ConversationHandler.END

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
            )
        else:
            reply_text=IAM_SORRY

            await update.message.reply_text(
                text=reply_text,
            )

        db.close()

    async def respond_in_private_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_chat.id

        word = update.message.text
        await self.translate(update, context, word_to_trans=word)

    async def respond_in_group_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message.text

        if message.startswith(TRANSLATE_COMMAND):
            word = message.split()[1]
            await self.translate(update, context, word_to_trans=word)

    async def is_user_joined(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_id = update.effective_user.id

        if query is None:
            return
        
        data = query.data
        if data == JOINED:
            user_member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
            if user_member.status in USER_STATUS:
                markup = InlineKeyboardMarkup(ADD_TO_GROUP_KEYBOARD)
                await query.answer(JOIN_SUCCESS, show_alert=True)
                await query.edit_message_text(HELP_MESSAGE, reply_markup=markup)

            else:
                await query.answer(JOIN_FAILED, show_alert=True)

    def remove_h_tags(self, word):
        new_word = re.sub(r'<h1>.*?</h1>', '', word)
        return new_word
