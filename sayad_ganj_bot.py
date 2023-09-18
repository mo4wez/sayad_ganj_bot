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
from constants.messages import (
    WELCOME_TEXT,
    TRANSLATE_COMMAND,
    YOU,
    IAM_SORRY,
    ASKED,
    ARROW_DOWN,
    CHANNEL_USERNAME,
    USER_STATUS,
    FORCE_JOIN_TEXT,
    IAM_JOINED,
    JOIN_SUCCESS,
    JOIN_FAILED,
    HELP_MESSAGE,
    )
from constants.keyboards import FORCE_JOIN_KEYBOARD, ADD_TO_GROUP_KEYBOARD
from config import SayadGanjConfig
from database.db_core import WordBook, db
import re
from time import time


class SayadGanjBot:
    def __init__(self):
        self.config = SayadGanjConfig()
        self.bot = Application.builder().token(self.config.token).build()
        self.START = range(1)

        print('init')

    def run(self):
        self.bot.add_handler(
            ConversationHandler(
                entry_points=[CommandHandler(command='start', callback=self.start)],

                states = {
                    self.START: [MessageHandler(filters=filters.TEXT, callback=self.start)]
                },

                fallbacks = [
                    CommandHandler(command='start', callback=self.start)
                ]
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
            CallbackQueryHandler(callback=self.is_user_joined)
        )

        self.bot.run_polling()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_chat.id
        user_status = await context.bot.get_chat_member(
            chat_id=CHANNEL_USERNAME,
            user_id=user_id,
        )

        if update.message.text == "/start":
            if user_status.status not in USER_STATUS:
                markup = InlineKeyboardMarkup(FORCE_JOIN_KEYBOARD)
                print('in start')

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

        return self.START

    async def translate(self, update: Update, context: ContextTypes.DEFAULT_TYPE, word_to_trans):
        message = word_to_trans

        if message:
            word_for_translate = message

            self.results = WordBook.select().where(
                WordBook.langFullWord == word_for_translate
            )
            print(len(self.results))

            if self.results:
                reply_text = ''
                for result in self.results:
                    cleaned_translation = self.remove_h_tags(result.entry)
                    
                    if len(self.results) > 1:
                        reply_text += cleaned_translation + '\n'
                    else:
                        reply_text += cleaned_translation

                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=reply_text,
                )

            else:
                reply_text=IAM_SORRY

                await context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text=reply_text,
                )

        db.close()


    async def respond_in_private_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        word = update.message.text
        await self.translate(update, context, word_to_trans=word)

    async def respond_in_group_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message.text
        print('in group def')
        if message.startswith(TRANSLATE_COMMAND):
            word = message.split()[:3]
            print(word)

            await self.translate(update, context, word_to_trans=word[1])

    async def is_user_joined(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_id = update.effective_user.id

        if query is None:
            return
        
        data = query.data
        if data == IAM_JOINED:
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
