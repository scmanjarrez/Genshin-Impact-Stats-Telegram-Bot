# SPDX-License-Identifier: MIT

# Copyright (c) 2021 scmanjarrez. All rights reserved.
# This work is licensed under the terms of the MIT license.

from telegram.error import BadRequest
from telegram import ParseMode
from enum import Enum
import traceback
import time
import re


CHAR = re.compile(r"Side_(.*)\.png")


class CMD(Enum):
    NOP = ''
    GIFT = 'redeem'
    AUTH = 'auth'


def uid(update):
    return update.effective_message.chat.id


def send(update, msg, quote=True, reply_markup=None):
    update.message.reply_html(msg, quote=quote, reply_markup=reply_markup,
                              disable_web_page_preview=True)


def send_bot(bot, uid, msg, reply_markup=None):
    bot.send_message(uid, msg, ParseMode.HTML, reply_markup=reply_markup,
                     disable_web_page_preview=True)


def edit(update, msg, reply_markup):
    try:
        update.callback_query.edit_message_text(msg, ParseMode.HTML,
                                                reply_markup=reply_markup,
                                                disable_web_page_preview=True)
    except BadRequest as br:
        if not str(br).startswith("Message is not modified:"):
            print(f"***  Exception caught in edit "
                  f"({update.effective_message.chat.id}): ", br)
            traceback.print_stack()


def fmt_sec(seconds):
    return time.strftime("%H:%M:%S", time.gmtime(int(seconds)))


def fmt_exp(expeditions):
    char_info = []
    for exp in expeditions:
        name = re.search(CHAR, exp['icon']).group(1)
        remain = (fmt_sec(exp['remaining_time']) if exp['remaining_time'] != 0
                  else 'Finished')
        char_info.append(f"    - {name} => <code>{remain}</code>\n")
    return "".join(char_info)
