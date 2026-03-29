#!/usr/bin/env python3
"""
Remnawave - Create Test User
Usage: python create_test_user.py
"""

import sys
import os
from datetime import datetime, timezone, timedelta

try:
    import requests
except ImportError:
    sys.exit("❌  requests not installed. Run: pip install requests")

try:
    from dotenv import load_dotenv
except ImportError:
    sys.exit("❌  python-dotenv not installed. Run: pip install python-dotenv")

# ── Load .env ──────────────────────────────────────────────────────────────────
load_dotenv()

def require_env(key: str) -> str:
    val = os.getenv(key, "").strip()
    if not val:
        sys.exit(f"❌  Missing required env variable: {key}")
    return val

def optional_env(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()

BASE_URL          = require_env("REMNAWAVE_BASE_URL").rstrip("/")
TOKEN             = require_env("REMNAWAVE_TOKEN")
TAG               = optional_env("TEST_TAG")
INTERNAL_SQUAD    = optional_env("TEST_INTERNAL_SQUAD_UUID")   # comma-separated UUIDs ok
EXTERNAL_SQUAD    = optional_env("TEST_EXTERNAL_SQUAD_UUID")
TRAFFIC_LIMIT_GB  = float(optional_env("TEST_TRAFFIC_LIMIT_GB", "1"))
EXPIRE_DAYS       = int(optional_env("TEST_EXPIRE_DAYS", "3"))
RESET_STRATEGY    = optional_env("TEST_TRAFFIC_RESET_STRATEGY", "NO_RESET")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

# ── Helpers ────────────────────────────────────────────────────────────────────
def gb_to_bytes(gb: float) -> int:
    return int(gb * 1024 ** 3)

def expire_iso(days: int) -> str:
    dt = datetime.now(timezone.utc) + timedelta(days=days)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")

def api(method: str, path: str, **kwargs):
    url = f"{BASE_URL}{path}"
    resp = requests.request(method, url, headers=HEADERS, timeout=15, **kwargs)
    if not resp.ok:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        sys.exit(f"❌  API error [{resp.status_code}] {path}\n    {detail}")
    return resp.json()

def separator():
    print("─" * 48)

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    separator()
    print("  🛠   Remnawave — Create Test User")
    separator()

    # Ask for username
    username = input("  Username: ").strip()
    if not username:
        sys.exit("❌  Username cannot be empty.")

    print()
    print("  Creating user …")

    # Build request body
    body: dict = {
        "username": username,
        "trafficLimitBytes": gb_to_bytes(TRAFFIC_LIMIT_GB),
        "trafficLimitStrategy": RESET_STRATEGY,
        "expireAt": expire_iso(EXPIRE_DAYS),
    }

    if TAG:
        body["tag"] = TAG

    if EXTERNAL_SQUAD:
        body["externalSquadUuid"] = EXTERNAL_SQUAD

    # Internal squads — send as list
    if INTERNAL_SQUAD:
        uuids = [u.strip() for u in INTERNAL_SQUAD.split(",") if u.strip()]
        body["activeUserInbounds"] = uuids   # field name used by Remnawave API

    # POST /api/users
    data = api("POST", "/api/users", json=body)
    user = data.get("response", data)

    # If internal squad wasn't accepted in body, add via squad endpoint
    if INTERNAL_SQUAD and not user.get("internalSquads"):
        uuids = [u.strip() for u in INTERNAL_SQUAD.split(",") if u.strip()]
        for squad_uuid in uuids:
            try:
                api("POST", f"/api/internal-squads/{squad_uuid}/users", json={"uuids": [user["uuid"]]})
            except SystemExit:
                print(f"  ⚠️   Could not assign internal squad {squad_uuid} (skipped)")

    # ── Print result ────────────────────────────────────────────────────────────
    sub_url  = user.get("subscriptionUrl", "—")
    uuid     = user.get("uuid", "—")
    status   = user.get("status", "—")
    expire   = user.get("expireAt", "—")
    traffic  = user.get("trafficLimitBytes", 0)
    tag_out  = user.get("tag", "—")

    traffic_gb = traffic / 1024 ** 3 if traffic else 0

    print()
    separator()
    print(f"  ✅  User created successfully")
    separator()
    print(f"  Username   : {user.get('username', username)}")
    print(f"  UUID       : {uuid}")
    print(f"  Status     : {status}")
    print(f"  Tag        : {tag_out}")
    print(f"  Traffic    : {traffic_gb:.2f} GB")
    print(f"  Expires    : {expire}")
    separator()
    print(f"  📎 Subscription URL:")
    print(f"  {sub_url}")
    separator()


if __name__ == "__main__":
    main()
