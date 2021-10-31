#!/usr/bin/env python3

# SPDX-License-Identifier: MIT

# Copyright (c) 2021 scmanjarrez. All rights reserved.
# This work is licensed under the terms of the MIT license.

from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater)
import paimon_cli as cli
import paimon_gui as gui
import util as ut
import logging
import os


def load_config():
    with open(".config", 'r') as f:
        config = {k: v for k, v in
                  [line.split('=') for line in f.read().splitlines()]}
    return config


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
        config = load_config()

        updater = Updater(token=config['apikey'], use_context=True)
        dispatcher = updater.dispatcher

        setup_handlers(dispatcher, updater.job_queue)

        updater.start_webhook(listen=config['listen'],
                              port=config['port'],
                              url_path=config['apikey'],
                              key=config['key'],
                              cert=config['cert'],
                              webhook_url=(f"https://"
                                           f"{config['ip']}:"
                                           f"{config['port']}/"
                                           f"{config['apikey']}"))
        updater.idle()
    else:
        print("File .config not found.")
