# SPDX-License-Identifier: MIT

# Copyright (c) 2021 scmanjarrez. All rights reserved.
# This work is licensed under the terms of the MIT license.

import genshinstats.errors as err
import genshinstats as gs
import paimon_gui as gui
import util as ut


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


def _redeem(code, msg):
    try:
        gs.redeem_code(code)
        msg = "Coded redeemed successfully."
    except err.CodeRedeemException:
        pass
    return msg


def redeem(update, context):
    uid = ut.uid(update)
    if allowed(uid):
        msg = "❗ Argument must be a valid code."
        if context.args:
            msg = _redeem(context.args[0], msg)
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
                msg = "❗ Argument must be a valid code."
                _redeem(args[0], msg)
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
