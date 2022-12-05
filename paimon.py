#!/usr/bin/env python3

# SPDX-License-Identifier: MIT

# Copyright (c) 2021-2022 scmanjarrez. All rights reserved.
# This work is licensed under the terms of the MIT license.

from telegram.ext import (ApplicationBuilder, CallbackQueryHandler,
                          CommandHandler, filters)
from telegram import Update

import paimon_cli as cli
import paimon_gui as gui
import utils as ut
import logging
import os


async def button_handler(update: Update, context: ut.Context):
    uid = ut.uid(update)
    query = update.callback_query
    if cli.allowed(uid):
        if query.data == 'main_menu':
            await gui.main_menu(update)
        elif query.data == 'notes_menu':
            await gui.notes_menu(update, context)
        elif query.data == 'diary_month_menu':
            await gui.diary_month_menu(update)
        elif query.data.startswith('diary_menu'):
            args = query.data.split('_')
            await gui.diary_menu(update, int(args[-1]))
        elif query.data == 'abyss_seasons_menu':
            await gui.abyss_seasons_menu(update)
        elif query.data.startswith('abyss_floors_menu'):
            args = query.data.split('_')
            await gui.abyss_floors_menu(update, args[-1] == 'previous')
        elif query.data.startswith('abyss_menu'):
            args = query.data.split('_')
            await gui.abyss_menu(update, args[-2] == 'previous', args[-1])
        elif query.data == 'notifications_menu':
            await gui.notifications_menu(update)
        elif query.data.startswith('notification_toggle'):
            args = query.data.split('_')
            await gui.notification_toggle(update, args[-1])


def setup_handlers(application: ApplicationBuilder):
    start_handler = CommandHandler(
        'start', cli.bot_help,
        filters=~filters.UpdateType.EDITED_MESSAGE)
    application.add_handler(start_handler)

    help_handler = CommandHandler(
        'help', cli.bot_help,
        filters=~filters.UpdateType.EDITED_MESSAGE)
    application.add_handler(help_handler)

    menu_handler = CommandHandler(
        'menu', cli.menu,
        filters=~filters.UpdateType.EDITED_MESSAGE)
    application.add_handler(menu_handler)

    redeem_handler = CommandHandler(
        'redeem', cli.redeem,
        filters=~filters.UpdateType.EDITED_MESSAGE)
    application.add_handler(redeem_handler)

    set_handler = CommandHandler(
        'set', cli.set_value,
        filters=~filters.UpdateType.EDITED_MESSAGE)
    application.add_handler(set_handler)

    get_handler = CommandHandler(
        'get', cli.get_value,
        filters=~filters.UpdateType.EDITED_MESSAGE)
    application.add_handler(get_handler)

    application.add_handler(CallbackQueryHandler(button_handler))


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    if os.path.isfile(ut.CONF_FILE):
        ut.set_up()
        application = ApplicationBuilder().token(
            ut.setting('token')).build()
        application.job_queue.run_once(
            ut.update_db, 5, name='Starting DB update')
        application.job_queue.run_once(
            ut.daily_checkin, 10, name='Starting daily claiming')
        setup_handlers(application)

        application.run_webhook(
            listen=ut.setting('listen'),
            port=ut.setting('port'),
            url_path=ut.setting('token'),
            cert=ut.setting('cert'),
            webhook_url=(f"https://"
                         f"{ut.setting('ip')}/"
                         f"{ut.setting('token')}")
        )
        # application.run_polling()
    else:
        print(f"File {ut.CONF_FILE} not found.")
