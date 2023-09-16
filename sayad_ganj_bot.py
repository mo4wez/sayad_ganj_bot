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
    )
from config import SayadGanjConfig
from database.db_core import WordBook, db
import re
from time import time


class SayadGanjBot:
    def __init__(self):
        self.config = SayadGanjConfig()
        self.bot = Application.builder().token(self.config.token).build()

        print('init')

    def run(self):
        self.bot.add_handler(
            MessageHandler(
                filters=filters.ChatType.PRIVATE,
                callback=self.respond_in_private_chat,
            )
        )

        self.bot.add_handler(
            MessageHandler(
                filters=filters.ChatType.GROUPS,
                callback=self.respond_in_group_chat,
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
            CallbackQueryHandler(callback=self.show_translation_answer)
        )

        self.bot.run_polling()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=WELCOME_TEXT,
        )

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


    async def show_translation_answer(self, update: Update, context: CallbackContext):
        query = update.callback_query
        data = query.data
        print(f'data: {data}')

        definition = WordBook.select().where(WordBook._id == data)
        for defi in definition:
            entry = self.remove_h_tags(defi.entry)
            try:
                await query.edit_message_text(text=entry, reply_markup=self.markup)
            except TimeoutError:
                query.edit_message_text(text='Error', reply_markup=self.markup)

        db.close()

    def remove_h_tags(self, word):
        new_word = re.sub(r'<h1>.*?</h1>', '', word)
        return new_word
