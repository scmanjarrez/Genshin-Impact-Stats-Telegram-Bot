# SPDX-License-Identifier: MIT

# Copyright (c) 2021 scmanjarrez. All rights reserved.
# This work is licensed under the terms of the MIT license.

from telegram.error import BadRequest
from telegram import ParseMode
import genshinstats as gs
from enum import Enum
import traceback
import datetime
import pytz
import time
import re


CHAR = re.compile(r"Side_(.*)\.png")


class CMD(Enum):
    NOP = ''
    GIFT = 'redeem'


def uid(update):
    return update.effective_message.chat.id


def send(update, msg, button=False, quote=True, reply_markup=None):
    if button:
        update.callback_query.message.chat.send_message(msg)
    else:
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


def daily_callback(context):
    reward = gs.claim_daily_reward()
    if reward is None:
        print("Could not claim daily reward")


def daily_checkin(queue, uid):
    midnight = datetime.time(minute=10, tzinfo=pytz.timezone('Asia/Shanghai'))
    queue.run_daily(daily_callback, midnight, name='checkin')
