#!/usr/bin/env python3

# SPDX-License-Identifier: MIT

# Copyright (c) 2021 scmanjarrez. All rights reserved.
# This work is licensed under the terms of the MIT license.

from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater)
import genshinstats as gs
import paimon_cli as cli
import paimon_gui as gui
import util as ut
import logging
import os


CONFIG = None


def _load_config():
    global CONFIG
    if CONFIG is None:
        with open(".config", 'r') as f:
            CONFIG = {k: v for k, v in
                      [line.split('=') for line in f.read().splitlines()]}


def button_handler(update, context):
    uid = ut.uid(update)
    query = update.callback_query
    if cli.allowed(uid):
        if query.data == 'main_menu':
            gui.main_menu(update)
        elif query.data == 'notes_menu':
            gui.notes_menu(update)
        elif query.data == 'abyss_menu':
            gui.abyss_menu(update)
        elif query.data == 'settings_menu':
            gui.settings_menu(update)


def setup_handlers(dispatch, job_queue):
    start_handler = CommandHandler('start', cli.bot_help,
                                   filters=~Filters.update.edited_message)
    dispatch.add_handler(start_handler)

    help_handler = CommandHandler('help', cli.bot_help,
                                  filters=~Filters.update.edited_message)
    dispatch.add_handler(help_handler)

    menu_handler = CommandHandler('menu', cli.menu,
                                  filters=~Filters.update.edited_message)
    dispatch.add_handler(menu_handler)

    redeem_handler = CommandHandler('redeem', cli.redeem,
                                    filters=~Filters.update.edited_message)
    dispatch.add_handler(redeem_handler)

    cancel_handler = CommandHandler('cancel', cli.cancel,
                                    filters=~Filters.update.edited_message)
    dispatch.add_handler(cancel_handler)

    text_handler = MessageHandler(
        Filters.text & ~Filters.update.edited_message, cli.text)
    dispatch.add_handler(text_handler)

    dispatch.add_handler(CallbackQueryHandler(button_handler))


if __name__ == '__main__':
    logging.basicConfig(format=('%(asctime)s - %(name)s - '
                                '%(levelname)s - %(message)s'),
                        level=logging.INFO)

    if os.path.isfile('.config'):
        _load_config()
        gs.set_cookie(ltoken=CONFIG['ltoken'],
                      ltuid=CONFIG['ltuid'],
                      account_id=CONFIG['ltuid'],
                      cookie_token=CONFIG['ctoken'])

        updater = Updater(token=CONFIG['apikey'], use_context=True)
        dispatcher = updater.dispatcher

        ut.daily_checkin(updater.job_queue, CONFIG['uid'])
        setup_handlers(dispatcher, updater.job_queue)

        updater.start_webhook(listen=CONFIG['listen'],
                              port=CONFIG['port'],
                              url_path=CONFIG['apikey'],
                              key=CONFIG['key'],
                              cert=CONFIG['cert'],
                              webhook_url=(f"https://"
                                           f"{CONFIG['ip']}:"
                                           f"{CONFIG['port']}/"
                                           f"{CONFIG['apikey']}"))
        updater.idle()
    else:
        print("File .CONFIG not found.")
