from __future__ import annotations
from typing import Any, Iterable
from zoreza.db.core import connect, now_iso
from zoreza.db.connection_pool import get_connection

def fetchall(sql: str, params: tuple = ()) -> list[dict]:
    """Ejecuta SELECT y retorna todas las filas. Usa connection pooling."""
    with get_connection() as con:
        rows = con.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

def fetchone(sql: str, params: tuple = ()) -> dict | None:
    """Ejecuta SELECT y retorna una fila. Usa connection pooling."""
    with get_connection() as con:
        r = con.execute(sql, params).fetchone()
        return dict(r) if r else None

def execute(sql: str, params: tuple = ()) -> None:
    """Ejecuta INSERT/UPDATE/DELETE. Usa connection pooling."""
    with get_connection() as con:
        con.execute(sql, params)
        con.commit()

def executemany(sql: str, seq_params: Iterable[tuple]) -> None:
    """Ejecuta múltiples INSERT/UPDATE/DELETE. Usa connection pooling."""
    with get_connection() as con:
        con.executemany(sql, seq_params)
        con.commit()

def execute_returning_id(sql: str, params: tuple = ()) -> int:
    """Ejecuta INSERT y retorna el ID generado. Usa connection pooling."""
    with get_connection() as con:
        cur = con.execute(sql, params)
        con.commit()
        return int(cur.lastrowid)
