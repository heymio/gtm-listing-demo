#!/usr/bin/env python3
"""Resolve whether a recorded generic channel/account capability can be reused."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any


def _as_utc_date(value: datetime) -> date:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).date()


def resolve_capability(
    profile: dict[str, Any] | None,
    capability: str,
    *,
    now: datetime,
    max_age_days: int,
    expected_channel: str | None = None,
    expected_account_scope: str | None = None,
    conflicting: bool = False,
) -> dict[str, Any]:
    if not isinstance(capability, str) or not capability.strip():
        return {"status": "VERIFY", "value": None, "reason": "capability name invalid"}
    if not isinstance(max_age_days, int) or isinstance(max_age_days, bool) or max_age_days < 0:
        return {"status": "VERIFY", "value": None, "reason": "freshness window invalid"}
    if conflicting:
        return {"status": "VERIFY", "value": None, "reason": "conflicting evidence"}
    if not isinstance(profile, dict):
        return {"status": "VERIFY", "value": None, "reason": "capability profile missing"}

    if expected_channel is not None and profile.get("channel") != expected_channel:
        return {"status": "VERIFY", "value": None, "reason": "channel scope mismatch"}
    if expected_account_scope is not None and profile.get("account_scope") != expected_account_scope:
        return {"status": "VERIFY", "value": None, "reason": "account scope mismatch"}

    capabilities = profile.get("capabilities")
    if not isinstance(capabilities, dict) or capability not in capabilities:
        return {"status": "VERIFY", "value": None, "reason": "capability not recorded"}
    value = capabilities.get(capability)
    if not isinstance(value, bool):
        return {"status": "VERIFY", "value": None, "reason": "capability value invalid"}

    verified_at = profile.get("verified_at")
    if not isinstance(verified_at, str) or not verified_at:
        return {"status": "VERIFY", "value": None, "reason": "verification date missing"}
    try:
        verified_date = date.fromisoformat(verified_at)
    except ValueError:
        return {"status": "VERIFY", "value": None, "reason": "verification date invalid"}

    age_days = (_as_utc_date(now) - verified_date).days
    if age_days < 0:
        return {"status": "VERIFY", "value": None, "reason": "verification date is in the future"}
    if age_days > max_age_days:
        return {"status": "VERIFY", "value": None, "reason": "capability record stale"}

    return {"status": "REUSE", "value": value, "reason": "recent confirmed capability"}
