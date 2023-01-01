# SPDX-License-Identifier: MIT

# Copyright (c) 2021-2023 scmanjarrez. All rights reserved.
# This work is licensed under the terms of the MIT license.

from telegram import Bot, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, JobQueue
from telegram.constants import ParseMode
from telegram.error import BadRequest
from typing import List, Tuple, Union
from enum import Enum

import paimon_gui as gui
import database as db
import traceback
import calendar
import datetime
import genshin
import json
import pytz


# Global
CONF_FILE = '.config.json'
CONFIG = None
CLIENT = {}
MAX_RESIN = 160
FLOORS = ('9', '10', '11', '12')

# Type aliases
Context = ContextTypes.DEFAULT_TYPE
TimeDelta = datetime.timedelta
ExpChars = List[genshin.models.genshin.chronicle.notes.Expedition]
Floors = List[genshin.models.genshin.chronicle.abyss.Floor]
Battles = List[genshin.models.genshin.chronicle.abyss.Battle]
Stats = genshin.models.genshin.chronicle.abyss.CharacterRanks
StatChars = List[genshin.models.genshin.chronicle.abyss.AbyssRankCharacter]


class CMD(Enum):
    NOP = ''
    GIFT = 'redeem'
    RESIN = 'resin'
    TEAPOT = 'teapot'
    UPDATES = 'updates'


class Notes():
    def __init__(self, data):
        self.data = data

    @property
    def notes(self) -> genshin.models.genshin.chronicle.notes.Notes:
        return self.data

    @notes.setter
    def notes(self,
              data: genshin.models.genshin.chronicle.notes.Notes) -> None:
        self.data = data

    @property
    def resin(self) -> int:
        return self.data.current_resin

    @property
    def resin_max(self) -> int:
        return self.data.max_resin

    @property
    def resin_time(self) -> TimeDelta:
        return self.data.remaining_resin_recovery_time

    @property
    def teapot(self) -> int:
        return self.data.current_realm_currency

    @property
    def teapot_max(self) -> int:
        return self.data.max_realm_currency

    @property
    def teapot_time(self) -> TimeDelta:
        return self.data.remaining_realm_currency_recovery_time

    @property
    def teapot_seconds(self) -> int:
        return (self.teapot_time.days * 24 * 60 * 60 +
                self.teapot_time.seconds)

    @property
    def parametric_time(self) -> TimeDelta:
        return self.data.remaining_transformer_recovery_time

    @property
    def commissions(self) -> int:
        return self.data.completed_commissions

    @property
    def commissions_max(self) -> int:
        return self.data.max_commissions

    @property
    def commissions_claimed(self) -> str:
        return ('Claimed' if self.data.claimed_commission_reward
                else 'Unclaimed')

    @property
    def weeklies(self) -> int:
        return self.data.remaining_resin_discounts

    @property
    def weeklies_max(self) -> int:
        return self.data.max_resin_discounts

    @property
    def expeditions(self) -> ExpChars:
        return self.data.expeditions

    @property
    def expeditions_max(self) -> TimeDelta:
        return max(self.data.expeditions,
                   key=lambda x: x.remaining_time.seconds).remaining_time


def set_up() -> None:
    db.setup_db()
    global CONFIG, CLIENT
    with open(CONF_FILE) as f:
        CONFIG = json.load(f)
    for acc in CONFIG['accounts']:
        CLIENT[acc] = genshin.Client(
            {
                'ltoken': account(acc, 'ltoken'),
                'ltuid': account(acc, 'ltuid'),
                'account_id': account(acc, 'ltuid'),
                'cookie_token': account(acc, 'ctoken')
            }
        )
        CLIENT[acc].default_game = 'genshin'
        if not db.cached(acc):
            db.add_user(acc)


def setting(key: str) -> str:
    return CONFIG['settings'][key]


def account(uid: str, key: str) -> Union[str, int]:
    return CONFIG['accounts'][uid][key]


def uid(update: Update) -> str:
    return str(update.effective_message.chat.id)


async def send(update: Update, msg: str, button: bool = False,
               quote: bool = True,
               reply_markup: InlineKeyboardMarkup = None) -> None:
    if button:
        await (update
               .callback_query
               .message.chat.send_message(msg, ParseMode.HTML))
    else:
        await (update
               .message
               .reply_html(msg, quote=quote, reply_markup=reply_markup,
                           disable_web_page_preview=True))


async def send_bot(bot: Bot, uid: int, msg: str,
                   reply_markup: InlineKeyboardMarkup = None) -> None:
    await (bot
           .send_message(uid, msg, ParseMode.HTML, reply_markup=reply_markup,
                         disable_web_page_preview=True))


async def edit(update: Update, msg: str,
               reply_markup: InlineKeyboardMarkup = None) -> None:
    try:
        await (update
               .callback_query
               .edit_message_text(msg, ParseMode.HTML,
                                  reply_markup=reply_markup,
                                  disable_web_page_preview=True))
    except BadRequest as br:
        if not str(br).startswith("Message is not modified:"):
            print(f"***  Exception caught in edit "
                  f"({update.effective_message.chat.id}): ", br)
            traceback.print_stack()


def _remove_job(queue: JobQueue, name: str) -> None:
    current_jobs = queue.get_jobs_by_name(name)
    if current_jobs:
        for job in current_jobs:
            # print(f"INFO: Removing job: {name}")
            job.schedule_removal()


async def updatedb_callback(context: Context = None) -> None:
    for uid in CLIENT:
        _, notes_data = await notes(uid)
        db.set_teapot_max(uid, notes_data.teapot_max)


async def update_db(context: Context) -> None:
    await updatedb_callback()


async def daily_callback(context: Context = None) -> None:
    for uid, client in CLIENT.items():
        try:
            # reward = await client.claim_daily_reward()
            await client.claim_daily_reward()
        except genshin.AlreadyClaimed:
            # print(f"INFO: Daily already claimed: {uid}")
            pass
        else:
            # print(f"INFO: Claimed {reward.amount}x {reward.name}")
            pass


async def daily_checkin(context: Context) -> None:
    await daily_callback()
    midnight = datetime.time(
        minute=10, tzinfo=pytz.timezone('Asia/Shanghai'))
    context.job_queue.run_daily(
        daily_callback, midnight, name='daily_checkin')


async def update_notes(context: Context) -> None:
    await gui.update_notes(context.job.data, context)


def autoupdate_notes(update: Update, context: Context) -> None:
    queue = context.job_queue
    _remove_job(queue, f'autoupdate_notes_{uid(update)}')
    queue.run_repeating(
        update_notes, db.updates(uid(update)) * 60,
        name=f'autoupdate_notes_{uid(update)}', data=update)


def resin_time(update: Update) -> Tuple[int, int]:
    resin = db.resin(uid(update))
    return resin, ((MAX_RESIN - resin) * 8 * 60)


async def notify_resin(context: Context) -> None:
    update = context.job.data
    msg, notes_data = await notes(uid(update))
    seconds = notes_data.resin_time.seconds
    if not seconds:
        await send(update, "‼ Hey, your resin has reached the cap!",
                   button=True)
    else:
        resin, warn_seconds = resin_time(update)
        if seconds <= warn_seconds:
            await send(update, f"⚠️ Hey, your resin is over {resin}!",
                       button=True)
        notifier_resin(
            update, context, notes_data.resin_time)
    await gui.update_notes(update, context, (msg, notes_data))


def notifier_resin(update: Update, context: Context,
                   resin: TimeDelta) -> None:
    queue = context.job_queue
    _remove_job(queue, f'resin_{uid(update)}')
    if db.resin_warn(uid(update)) == 1:
        if resin.seconds:
            _, warn_seconds = resin_time(update)
            warn = resin.seconds - warn_seconds
            if warn <= 0:
                warn = resin.seconds
            queue.run_once(
                notify_resin, warn,
                name=f'resin_{uid(update)}', data=update)


def teapot_time(update: Update, data: Notes) -> Tuple[int, int]:
    _uid = uid(update)
    coin_sec = (data.teapot_max - data.teapot) / data.teapot_seconds
    seconds = (db.teapot_max(_uid) - db.teapot(_uid)) // coin_sec
    return data.teapot, seconds


async def notify_teapot(context: Context) -> None:
    update = context.job.data
    msg, notes_data = await notes(uid(update))
    if not notes_data.teapot_seconds:
        await send(update, "‼ Hey, your teapot currency has reached the cap!",
                   button=True)
    else:
        teapot, warn_seconds = teapot_time(update, notes_data)
        if notes_data.teapot_seconds <= warn_seconds:
            await send(update,
                       f"⚠️ Hey, your teapot currency is over {teapot}!",
                       button=True)
        notifier_teapot(
            update, context, notes_data)
    await gui.update_notes(update, context, (msg, notes_data))


def notifier_teapot(update: Update, context: Context,
                    data: Notes) -> None:
    queue = context.job_queue
    _remove_job(queue, f'teapot_{uid(update)}')
    if db.teapot_warn(uid(update)) == 1:
        if data.teapot_seconds:
            _, warn_seconds = teapot_time(update, data)
            warn = data.teapot_seconds - warn_seconds
            if warn <= 0:
                warn = data.teapot_seconds
            queue.run_once(
                notify_teapot, warn,
                name=f'teapot_{uid(update)}', data=update)


async def notify_parametric(context: Context) -> None:
    update = context.job.data
    await send(update, "‼ Hey, your parametric is out of cooldown!",
               button=True)


def notifier_parametric(update: Update, context: Context,
                        parametric: TimeDelta) -> None:
    queue = context.job_queue
    if parametric is not None:
        if db.parametric_warn(uid(update)) == 1:
            noti = False
            if not queue.get_jobs_by_name(f'parametric_{uid(update)}'):
                if parametric.days:
                    parametric = TimeDelta(days=parametric.days+1)
                    noti = True
                if noti or parametric.seconds:
                    queue.run_once(
                        notify_parametric, parametric,
                        name=f'parametric_{uid(update)}', data=update)


async def notify_expedition(context: Context) -> None:
    update = context.job.data
    await send(update, "‼ Hey, all your expeditions have finished!",
               button=True)


def notifier_expedition(update: Update, context: Context,
                        expedition: TimeDelta) -> None:
    queue = context.job_queue
    _remove_job(queue, f'expedition_{uid(update)}')
    if db.expedition_warn(uid(update)) == 1:
        if expedition.seconds:
            queue.run_once(
                notify_expedition, expedition,
                name=f'expedition_{uid(update)}', data=update)


def last_updated() -> str:
    return datetime.datetime.now(
        pytz.timezone(setting('timezone'))).strftime('%Y/%m/%d %H:%M:%S')


async def redeem(uid: str, code: str) -> None:
    try:
        await CLIENT[uid].redeem_code(code)
    except genshin.errors.RedemptionException as e:
        msg = e.msg
    else:
        msg = "Code redeemed successfully."
    return msg


async def notes(uid: str) -> Tuple[str, Notes]:
    data = await CLIENT[uid].get_genshin_notes(account(uid, 'uid'))
    data = Notes(data)
    msg = (
        f"<b>Resin:</b> "
        f"<code>"
        f"{data.resin}/{data.resin_max} ({data.resin_time})"
        f"</code>\n"

        f"<b>Teapot Currency:</b> "
        f"<code>"
        f"{data.teapot}/{data.teapot_max} ({data.teapot_time})"
        f"</code>\n"

        f"<b>Parametric Transformer:</b> "
        f"<code>"
        f"{data.parametric_time}"
        f"</code>\n"

        f"<b>Commissions:</b> "
        f"<code>"
        f"{data.commissions}/{data.commissions_max} "
        f"({data.commissions_claimed})"
        f"</code>\n"

        f"<b>Weekly Boss Discounts:</b> "
        f"<code>"
        f"{data.weeklies}/{data.weeklies_max}"
        f"</code>\n"

        f"<b>Expeditions:</b>\n"
        f"{fmt_exp_chars(data.expeditions)}\n"

        f"<b>Last updated</b>: <code>{last_updated()}</code>"
    )
    return (msg, data)


def fmt_exp_chars(characters: ExpChars) -> str:
    exp = [f"    - {chr.character.name} => "
           f"<code>"
           f"{chr.remaining_time if not chr.finished else 'Finished'}"
           f"</code>\n"
           for chr in characters]
    return "".join(exp)


async def diary(uid: str, month: int) -> str:
    info = await CLIENT[uid].get_diary(month=month)
    msg = [f"<b>Primogems earned in {calendar.month_name[month]}</b>: "
           f"<code>{info.data.current_primogems}</code>"]
    for category in info.data.categories:
        msg.append(f"    - {category.name}: "
                   f"<code>{category.amount} "
                   f"({category.percentage} %)</code>")
    return "\n".join(msg)


async def abyss(uid: str, previous: bool = False, floor: str = 'all') -> str:
    data = await CLIENT[uid].get_spiral_abyss(
        account(uid, 'uid'), previous=previous)
    sea = "Current"
    if previous:
        sea = 'Previous'

    msg = (f"⚜ <b>{sea} Season</b> ⚜\n\n"
           f"<b>Summary</b>:\n"
           f"    - <b>Deepest Descent:</b> "
           f"<code>"
           f"{data.max_floor}"
           f"</code>\n"

           f"    - <b>Battles Fought:</b> "
           f"<code>"
           f"{data.total_battles} ({data.total_stars} ⭐️)"
           f"</code>\n\n"

           f"{fmt_stats(data.ranks)}"


           f"{fmt_floors(data.floors, floor)}")
    return msg


def _floor(floors: Floors, floor: str) -> Floors:
    if floor in FLOORS:
        return [fl for fl in floors if str(fl.floor) == floor]
    else:
        return [fl for fl in floors if str(fl.floor) in FLOORS]


def fmt_floors(floors: Floors, floor: str) -> str:
    data = _floor(floors, floor)
    msg = ""
    parsed = "\n".join([
        "".join([(f"    - <b>{fl.floor} - {ch.chamber}</b>: "
                  f"{ch.stars}/{ch.max_stars} ⭐️\n"
                  f"{fmt_battle_chars(ch.battles)}\n")
                 for ch in fl.chambers])
        for fl in data])
    if parsed:
        msg = f"<b>Floors:</b>\n{parsed}"
    return msg


def fmt_battle_chars(battles: Battles) -> str:
    msg = []
    for battle in battles:
        half = [char.name for char in battle.characters]
        msg.append(f"    » <code>{', '.join(half)}</code>")
    return "\n".join(msg)


def fmt_stats(stats: Stats) -> str:
    chars = sum([len(getattr(stats, category)) for category in stats.dict()])
    msg = ""
    if chars:
        msg = (f"<b>Stats</b>:\n"
               f"    - <b>Most played</b>:\n"
               f"{fmt_stat_chars(stats.most_played)}\n"
               f"    - <b>Most kills</b>:\n"
               f"{fmt_stat_chars(stats.most_kills)}\n"
               f"    - <b>Strongest strike</b>:\n"
               f"{fmt_stat_chars(stats.strongest_strike)}\n"
               f"    - <b>Most damage taken</b>:\n"
               f"{fmt_stat_chars(stats.most_damage_taken)}\n"
               f"    - <b>Most bursts used</b>:\n"
               f"{fmt_stat_chars(stats.most_bursts_used)}\n"
               f"    - <b>Most skills used</b>:\n"
               f"{fmt_stat_chars(stats.most_skills_used)}\n\n")
    return msg


def fmt_stat_chars(characters: StatChars) -> str:
    msg = []
    for ch in characters:
        msg.append(f"    » <code>{ch.name} ({ch.value})</code>")
    return "\n".join(msg)
