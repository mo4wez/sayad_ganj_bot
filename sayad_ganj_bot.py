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
            CallbackQueryHandler(callback=self.show_translation_answer)
        )

        self.bot.run_polling()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Hello there!"
        )

    async def translate(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message.text

        if message:
            word_for_translate = message

            results = WordBook.select().where(
                WordBook.langFullWord == word_for_translate
            )
            print(len(results))

            if results:
                buttons = []
                for result in results:
                    cleaned_description = self.remove_h_tags(result.entry)
                    new_trans = cleaned_description.split(':')[0].split('\n')[1]
                    word_id = str(result._id)

                    buttons.append(
                        [InlineKeyboardButton(f'{new_trans}', callback_data=word_id)]
                    )

                reply_text = YOU + word_for_translate + ASKED

                self.markup = InlineKeyboardMarkup(buttons)

                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=reply_text,
                    reply_markup=self.markup,
                )


            else:
                reply_text=IAM_SORRY

                await context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text=reply_text,
                )

        db.close()


    async def show_translation_answer(self, update: Update, context: CallbackContext):
        query = update.callback_query

        data = query.data
        print(data)

        definition = WordBook.select().where(WordBook._id == data)
        for defi in definition:
            print(defi.entry)
            entry = self.remove_h_tags(defi.entry)
            await query.edit_message_text(text=entry, reply_markup=self.markup)

        db.close()

    def remove_h_tags(self, word):
        new_word = re.sub(r'<h1>.*?</h1>', '', word)
        return new_word