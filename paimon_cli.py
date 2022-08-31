# SPDX-License-Identifier: MIT

# Copyright (c) 2021-2022 scmanjarrez. All rights reserved.
# This work is licensed under the terms of the MIT license.

from telegram import Update
import paimon_gui as gui
import utils as ut


STATE = ut.CMD.NOP
HELP = (
    "Hello Traveler, use the following commands to interact with me:"
    "\n\n"

    "❔ /menu - Interact with me using UI."
    "\n"
    "❔ /redeem <code>[#]</code> - Redeem the gift code."
    "\n\n"

    "<b>Bot Usage</b>\n"
    "❔ /help - List of commands."
    "\n"
    "❔ /cancel - Cancel current action."
    "\n\n"

    "<i><b>Note:</b> Arguments inside brackets are optional.</i>"
)


def _state(state: ut.CMD = ut.CMD.NOP) -> None:
    global STATE
    STATE = state


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
            msg = "Tell me the gift code to redeem:"
            _state(ut.CMD.GIFT)
        await ut.send(update, msg)


async def text(update: Update, context: ut.Context) -> None:
    uid = ut.uid(update)
    if allowed(uid):
        msg = "❗ Send only one argument."
        args = update.message.text.split()
        if len(args) == 1:
            if STATE == ut.CMD.GIFT:
                msg = await ut.redeem(uid, args[0])
            else:
                _state(uid)
        await ut.send(update, msg)


async def cancel(update: Update, context: ut.Context) -> None:
    uid = ut.uid(update)
    if allowed(uid):
        if STATE != ut.CMD.NOP:
            msg = (f"The command <code>{STATE.value}</code> "
                   f"has been cancelled. Anything else I can do for you?"
                   f"\n\n"
                   f"Send /help for a list of commands.")
            _state()
        else:
            msg = ("No active command to cancel. "
                   "I wasn't doing anything anyway.\nZzzzz...")
        await ut.send(update, msg)
