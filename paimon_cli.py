# SPDX-License-Identifier: MIT

# Copyright (c) 2021-2022 scmanjarrez. All rights reserved.
# This work is licensed under the terms of the MIT license.

from telegram import Update

import paimon_gui as gui
import database as db
import utils as ut


HELP = (
    "Hello Traveler, use the following commands to interact with me:"
    "\n\n"

    "❔ /menu - Interact with me using UI."
    "\n"
    "❔ /redeem <code>code</code> - Redeem the gift code."
    "\n"
    "❔ /set <code>type</code> <code>value</code> - Set "
    "<code>resin/teapot/updates</code> value. "
    "Default resin: 150. Default teapot: 2200. Default updates: 240"
    "\n\n"

    "<b>Bot Usage</b>\n"
    "❔ /help - List of commands."
    "\n\n"
)


def allowed(uid: str) -> bool:
    return uid in ut.CLIENT


async def bot_help(update: Update, context: ut.Context) -> None:
    uid = ut.uid(update)
    if allowed(uid):
        await ut.send(update, HELP)


async def menu(update: Update, context: ut.Context) -> None:
    uid = ut.uid(update)
    if allowed(uid):
        await gui.main_menu(update)


async def redeem(update: Update, context: ut.Context) -> None:
    uid = ut.uid(update)
    if allowed(uid):
        if context.args:
            msg = await ut.redeem(uid, context.args[0])
        else:
            msg = "Send the gift code to redeem, e.g. /redeem GENSHINGIFT"
        await ut.send(update, msg)


async def set_value(update: Update, context: ut.Context) -> None:
    uid = ut.uid(update)
    if allowed(uid):
        if context.args and len(context.args) == 2:
            try:
                value = int(context.args[1])
            except ValueError:
                msg = "Argument must be an integer."
            else:
                set_type = context.args[0]
                if set_type == 'resin':
                    if 0 < value < ut.MAX_RESIN:
                        db.set_resin(uid, value)
                        msg = (f"Resin notification threshold "
                               f"has been updated to {value}.")
                    else:
                        msg = (f"Resin notification threshold must be "
                               f"greater than 0 and lower than "
                               f"{ut.MAX_RESIN}.")
                elif set_type == 'teapot':
                    if 0 < value < db.teapot_max(uid) and not value % 30:
                        db.set_teapot(uid, value)
                        msg = (f"Teapot currency notification threshold "
                               f"has been updated to {value}.")
                    else:
                        msg = (f"Teapot currency notification threshold must "
                               f"be greater than 0, lower than "
                               f"{db.teapot_max(uid)} and multiple of 30.")
                elif set_type == 'updates':
                    if value > 0:
                        db.set_updates(uid, value)
                        msg = f"Updates interval has been updated to {value}."
                    else:
                        msg = "Updates interval must be greater than 0."
        else:
            msg = ("Send the type and value to be set: "
                   "resin, teapot or update, e.g. /set resin 120, "
                   "/set teapot 200")
        await ut.send(update, msg)
