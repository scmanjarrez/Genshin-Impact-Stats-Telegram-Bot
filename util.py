# SPDX-License-Identifier: MIT

# Copyright (c) 2021 scmanjarrez. All rights reserved.
# This work is licensed under the terms of the MIT license.

from telegram.error import BadRequest
from telegram import ParseMode
from enum import Enum

import configparser as cfg
import genshinstats as gs
import paimon_gui as gui
import traceback
import datetime
import pytz
import time
import re


CHAR = re.compile(r'Side_(.*)\.png')
UPD_NOTES = 4 * 60 * 60  # update every 4 hours
CONF_FILE = '.config'
_CONFIG = None
FLOORS = {'9': 0, '10': 1, '11': 2, '12': 3}


class CMD(Enum):
    NOP = ''
    GIFT = 'redeem'


def _load_config():
    global _CONFIG
    if _CONFIG is None:
        parser = cfg.ConfigParser()
        parser.read(CONF_FILE)
        _CONFIG = {k: v for section in parser.sections()
                   for k, v in parser[section].items()}


def config(key):
    _load_config()
    return _CONFIG[key]


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


def fmt_seconds(seconds):
    return time.strftime("%H:%M:%S", time.gmtime(int(seconds)))


def fmt_expeditions(expeditions):
    char_info = []
    for exp in expeditions:
        name = re.search(CHAR, exp['icon']).group(1)
        remain = (fmt_seconds(exp['remaining_time'])
                  if exp['remaining_time'] != 0 else 'Finished')
        char_info.append(f"    - {name} => <code>{remain}</code>\n")
    return "".join(char_info)


def fmt_floors(floors, floor):
    def parse_characters(battles):
        return " | ".join(
            [", ".join(
                [char['name'] for char in chamber['characters']]
            ) for chamber in battles])
    if floor in FLOORS:
        floors = [floors[FLOORS[floor]]]
    floor_info = []
    for fl in floors:
        for ch in fl['chambers']:
            floor_info.append(f"    - <b>{fl['floor']}-{ch['chamber']} "
                              f"({ch['stars']}/{ch['max_stars']}*):</b> "
                              f"<code>{parse_characters(ch['battles'])}"
                              f"</code>\n")
        floor_info.append("\n")
    return "".join(floor_info)


def _remove_job(queue, name):
    current_jobs = queue.get_jobs_by_name(name)
    if current_jobs:
        for job in current_jobs:
            job.schedule_removal()


def daily_callback(context):
    reward = gs.claim_daily_reward()
    if reward is None:
        send_bot(context.bot, config('admin'), "Could not claim daily reward.")


def daily_checkin(queue, uid):
    midnight = datetime.time(minute=10, tzinfo=pytz.timezone('Asia/Shanghai'))
    queue.run_daily(daily_callback, midnight, name='daily_checkin')


def update_notes(context):
    update = context.job.context
    gui.update_notes(update)


def autoupdate_notes(queue, update):
    _remove_job(queue, 'autoupdate_notes')
    queue.run_repeating(update_notes, UPD_NOTES,
                        context=update, name='autoupdate_notes')


def last_updated():
    return datetime.datetime.now(
        pytz.timezone(config('timezone'))).strftime('%Y/%m/%d %H:%M:%S')
