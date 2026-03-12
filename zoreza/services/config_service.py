from zoreza.db.queries import fetchall, fetchone, execute
from zoreza.db.core import now_iso

def get_config() -> dict[str, str]:
    rows = fetchall("SELECT key,value FROM config")
    return {r["key"]: r["value"] for r in rows}

def get_float(key: str, default: float) -> float:
    row = fetchone("SELECT value FROM config WHERE key=?", (key,))
    if not row:
        return default
    try:
        return float(row["value"])
    except Exception:
        return default

def set_config(key: str, value: str, user_id: int | None):
    execute(
        "INSERT INTO config(key,value,updated_at,updated_by) VALUES (?,?,?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at, updated_by=excluded.updated_by",
        (key, value, now_iso(), user_id),
    )
