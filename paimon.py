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


def button_handler(update, context):
    uid = ut.uid(update)
    query = update.callback_query
    if cli.allowed(uid):
        if query.data == 'main_menu':
            gui.main_menu(update)
        elif query.data == 'notes_menu':
            gui.notes_menu(update, context)
        elif query.data == 'abyss_seasons_menu':
            gui.abyss_seasons_menu(update)
        elif query.data.startswith('abyss_floors_menu'):
            args = query.data.split('_')
            gui.abyss_floors_menu(update, args[-1] == 'previous')
        elif query.data.startswith('abyss_menu'):
            args = query.data.split('_')
            gui.abyss_menu(update, args[-2] == 'previous', args[-1])


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

    if os.path.isfile(ut.CONF_FILE):
        gs.set_cookie(ltoken=ut.config('ltoken'),
                      ltuid=ut.config('ltuid'),
                      account_id=ut.config('ltuid'),
                      cookie_token=ut.config('ctoken'))

        updater = Updater(token=ut.config('bot'), use_context=True)
        dispatcher = updater.dispatcher
        setup_handlers(dispatcher, updater.job_queue)

        ut.daily_checkin(updater.job_queue, ut.config('uid'))

        updater.start_webhook(listen=ut.config('listen'),
                              port=ut.config('port'),
                              url_path=ut.config('bot'),
                              cert=ut.config('cert'),
                              webhook_url=(f"https://"
                                           f"{ut.config('ip')}/"
                                           f"{ut.config('bot')}")
                              )
        updater.idle()
    else:
        print(f"File {ut.CONF_FILE} not found.")
