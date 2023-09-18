from constants.messages import *

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    )

FORCE_JOIN_KEYBOARD = [
    [InlineKeyboardButton(text=TAKBAND_QANDEEL_CL, url=CHANNEL_URL)],
    [InlineKeyboardButton(text=IAM_JOINED, callback_data=JOINED)],
    ]

ADD_TO_GROUP_KEYBOARD = [
    [InlineKeyboardButton(text=ADD_TO_GROUP_MSG, url=ADD_TO_GROUP_URL)],
]