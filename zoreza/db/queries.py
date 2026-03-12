from __future__ import annotations
from typing import Any, Iterable
from zoreza.db.core import connect, now_iso

def fetchall(sql: str, params: tuple = ()) -> list[dict]:
    con = connect()
    try:
        rows = con.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        con.close()

def fetchone(sql: str, params: tuple = ()) -> dict | None:
    con = connect()
    try:
        r = con.execute(sql, params).fetchone()
        return dict(r) if r else None
    finally:
        con.close()

def execute(sql: str, params: tuple = ()) -> None:
    con = connect()
    try:
        con.execute(sql, params)
        con.commit()
    finally:
        con.close()

def executemany(sql: str, seq_params: Iterable[tuple]) -> None:
    con = connect()
    try:
        con.executemany(sql, seq_params)
        con.commit()
    finally:
        con.close()

def execute_returning_id(sql: str, params: tuple = ()) -> int:
    con = connect()
    try:
        cur = con.execute(sql, params)
        con.commit()
        return int(cur.lastrowid)
    finally:
        con.close()
