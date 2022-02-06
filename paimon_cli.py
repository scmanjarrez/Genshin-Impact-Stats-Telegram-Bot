# SPDX-License-Identifier: MIT

# Copyright (c) 2022 scmanjarrez. All rights reserved.
# This work is licensed under the terms of the MIT license.

import genshinstats.errors as err
import genshinstats as gs
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


def _state(state=ut.CMD.NOP):
    global STATE
    STATE = state


def allowed(uid):
    return uid == int(ut.config('admin'))


def bot_help(update, context):
    uid = ut.uid(update)
    if allowed(uid):
        ut.send(update, HELP)


def menu(update, context):
    uid = ut.uid(update)
    if allowed(uid):
        gui.main_menu(update)


def _redeem(code):
    try:
        gs.redeem_code(code)
    except err.GenshinStatsException as e:
        msg = e.msg
    else:
        msg = "Code redeemed successfully."
    return msg


def redeem(update, context):
    uid = ut.uid(update)
    if allowed(uid):
        if context.args:
            msg = _redeem(context.args[0])
        else:
            msg = "Tell me the gift code to redeem:"
            _state(ut.CMD.GIFT)
        ut.send(update, msg)


def text(update, context):
    uid = ut.uid(update)
    if allowed(uid):
        msg = "❗ Send only one argument."
        args = update.message.text.split()
        if len(args) == 1:
            if STATE == ut.CMD.GIFT:
                msg = _redeem(args[0])
            else:
                _state(uid)
        ut.send(update, msg)


def cancel(update, context):
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
        ut.send(update, msg)
