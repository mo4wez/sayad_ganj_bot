from constants.messages import *

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    )

TAKBAND_JOIN_KEYBOARD = [
    [InlineKeyboardButton(text=TAKBAND_QANDEEL_CL, url=CHANNEL_URL)],
]

ADD_TO_GROUP_KEYBOARD = [
    [InlineKeyboardButton(text=ADD_TO_GROUP_MSG, url=ADD_TO_GROUP_URL)],
]


TAKBAND_MARKUP = InlineKeyboardMarkup(TAKBAND_JOIN_KEYBOARD)
GROUP_MARKUP = InlineKeyboardMarkup(ADD_TO_GROUP_KEYBOARD)