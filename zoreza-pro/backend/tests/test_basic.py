"""Basic backend tests — validate imports and schema logic."""

from __future__ import annotations

from datetime import date

from app.services.corte_service import compute_week_bounds


def test_compute_week_bounds_monday():
    # 2024-04-01 is a Monday
    start, end = compute_week_bounds(date(2024, 4, 1))
    assert start == date(2024, 4, 1)
    assert end == date(2024, 4, 7)


def test_compute_week_bounds_friday():
    # 2024-04-05 is a Friday
    start, end = compute_week_bounds(date(2024, 4, 5))
    assert start == date(2024, 4, 1)
    assert end == date(2024, 4, 7)


def test_compute_week_bounds_sunday():
    # 2024-04-07 is a Sunday
    start, end = compute_week_bounds(date(2024, 4, 7))
    assert start == date(2024, 4, 1)
    assert end == date(2024, 4, 7)


def test_schema_validation():
    from app.schemas.corte import DetalleCapturadaPayload
    import uuid

    payload = DetalleCapturadaPayload(
        maquina_id=uuid.uuid4(),
        score_tarjeta=400.0,
        efectivo_total=500.0,
        fondo=100.0,
    )
    assert payload.score_tarjeta == 400.0


def test_password_hash():
    from app.core.security import hash_password, verify_password

    hashed = hash_password("test123")
    assert verify_password("test123", hashed)
    assert not verify_password("wrong", hashed)
