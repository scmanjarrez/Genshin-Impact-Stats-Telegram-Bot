#!/usr/bin/env python3

# SPDX-License-Identifier: MIT

# Copyright (c) 2021-2022 scmanjarrez. All rights reserved.
# This work is licensed under the terms of the MIT license.

from contextlib import closing

import sqlite3 as sql


DB = 'paimon.db'


def setup_db() -> None:
    with closing(sql.connect(DB)) as db:
        with closing(db.cursor()) as cur:
            cur.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    uid TEXT PRIMARY KEY,
                    resin_warn INTEGER DEFAULT 1,
                    resin INTEGER DEFAULT 150,
                    teapot_warn INTEGER DEFAULT 1,
                    teapot INTEGER DEFAULT 2200,
                    teapot_max INTEGER DEFAULT 0,
                    parametric_warn INTEGER DEFAULT 1,
                    expedition_warn INTEGER DEFAULT 1,
                    updates INTEGER DEFAULT 240
                );
                """
            )


def cached(uid: str) -> int:
    with closing(sql.connect(DB)) as db:
        with closing(db.cursor()) as cur:
            cur.execute(
                'SELECT EXISTS ('
                'SELECT 1 '
                'FROM users '
                'WHERE uid = ?'
                ')',
                [uid])
            return cur.fetchone()[0]


def add_user(uid: str) -> None:
    with closing(sql.connect(DB)) as db:
        with closing(db.cursor()) as cur:
            cur.execute('INSERT INTO users (uid) VALUES (?)',
                        [uid])
            db.commit()


def resin(uid: str) -> int:
    with closing(sql.connect(DB)) as db:
        with closing(db.cursor()) as cur:
            cur.execute(
                'SELECT resin '
                'FROM users '
                'WHERE uid = ?',
                [uid])
            return cur.fetchone()[0]


def set_resin(uid: str, value: int) -> None:
    with closing(sql.connect(DB)) as db:
        with closing(db.cursor()) as cur:
            cur.execute(
                'UPDATE users '
                'SET resin = ? '
                'WHERE uid = ?',
                [value, uid])
            db.commit()


def resin_warn(uid: str) -> int:
    with closing(sql.connect(DB)) as db:
        with closing(db.cursor()) as cur:
            cur.execute(
                'SELECT resin_warn '
                'FROM users '
                'WHERE uid = ?',
                [uid])
            return cur.fetchone()[0]


def toggle_resin_warn(uid: str) -> None:
    with closing(sql.connect(DB)) as db:
        with closing(db.cursor()) as cur:
            cur.execute(
                'UPDATE users '
                'SET resin_warn = -resin_warn '
                'WHERE uid = ?',
                [uid])
            db.commit()


def teapot(uid: str) -> int:
    with closing(sql.connect(DB)) as db:
        with closing(db.cursor()) as cur:
            cur.execute(
                'SELECT teapot '
                'FROM users '
                'WHERE uid = ?',
                [uid])
            return cur.fetchone()[0]


def set_teapot(uid: str, value: int) -> None:
    with closing(sql.connect(DB)) as db:
        with closing(db.cursor()) as cur:
            cur.execute(
                'UPDATE users '
                'SET teapot = ? '
                'WHERE uid = ?',
                [value, uid])
            db.commit()


def teapot_max(uid: str) -> int:
    with closing(sql.connect(DB)) as db:
        with closing(db.cursor()) as cur:
            cur.execute(
                'SELECT teapot_max '
                'FROM users '
                'WHERE uid = ?',
                [uid])
            return cur.fetchone()[0]


def set_teapot_max(uid: str, value: int) -> None:
    with closing(sql.connect(DB)) as db:
        with closing(db.cursor()) as cur:
            cur.execute(
                'UPDATE users '
                'SET teapot_max = ? '
                'WHERE uid = ?',
                [value, uid])
            db.commit()


def teapot_warn(uid: str) -> int:
    with closing(sql.connect(DB)) as db:
        with closing(db.cursor()) as cur:
            cur.execute(
                'SELECT teapot_warn '
                'FROM users '
                'WHERE uid = ?',
                [uid])
            return cur.fetchone()[0]


def toggle_teapot_warn(uid: str) -> None:
    with closing(sql.connect(DB)) as db:
        with closing(db.cursor()) as cur:
            cur.execute(
                'UPDATE users '
                'SET teapot_warn = -teapot_warn '
                'WHERE uid = ?',
                [uid])
            db.commit()


def parametric_warn(uid: str) -> int:
    with closing(sql.connect(DB)) as db:
        with closing(db.cursor()) as cur:
            cur.execute(
                'SELECT parametric_warn '
                'FROM users '
                'WHERE uid = ?',
                [uid])
            return cur.fetchone()[0]


def toggle_parametric_warn(uid: str) -> None:
    with closing(sql.connect(DB)) as db:
        with closing(db.cursor()) as cur:
            cur.execute(
                'UPDATE users '
                'SET parametric_warn = -parametric_warn '
                'WHERE uid = ?',
                [uid])
            db.commit()


def expedition_warn(uid: str) -> int:
    with closing(sql.connect(DB)) as db:
        with closing(db.cursor()) as cur:
            cur.execute(
                'SELECT expedition_warn '
                'FROM users '
                'WHERE uid = ?',
                [uid])
            return cur.fetchone()[0]


def toggle_expedition_warn(uid: str) -> None:
    with closing(sql.connect(DB)) as db:
        with closing(db.cursor()) as cur:
            cur.execute(
                'UPDATE users '
                'SET expedition_warn = -expedition_warn '
                'WHERE uid = ?',
                [uid])
            db.commit()


def updates(uid: str) -> int:
    with closing(sql.connect(DB)) as db:
        with closing(db.cursor()) as cur:
            cur.execute(
                'SELECT updates '
                'FROM users '
                'WHERE uid = ?',
                [uid])
            return cur.fetchone()[0]


def set_updates(uid: str, value: int) -> None:
    with closing(sql.connect(DB)) as db:
        with closing(db.cursor()) as cur:
            cur.execute(
                'UPDATE users '
                'SET updates = ? '
                'WHERE uid = ?',
                [value, uid])
            db.commit()
