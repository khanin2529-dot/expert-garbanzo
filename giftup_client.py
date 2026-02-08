# -*- coding: utf-8 -*-
"""
Simple Gift Up API client (placeholder).

Usage:
- Set environment variable `GIFTUP_TOKEN` with your API token.
- Configure `API_BASE` to the correct Gift Up API base URL.

This client provides `add_badge_to_profile(username, badge_name)` as a helper.

Note: Gift Up might not expose an API for profile badges; use this as a template
and adapt to the real API endpoints (or use browser automation fallback).
"""

import os
import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

API_BASE = os.getenv("GIFTUP_API_BASE", "https://api.giftup.com/v1")  # adjust if needed
TOKEN = os.getenv("GIFTUP_TOKEN")


class GiftUpClient:
    def __init__(self, token: str = None, api_base: str = None):
        self.api_base = api_base or API_BASE
        self.token = token or TOKEN
        if not self.token:
            logger.warning("No GIFTUP_TOKEN provided. Client will run in dry-run mode.")

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def add_badge_to_profile(self, username: str, badge_name: str, dry_run: bool = False) -> Dict[str, Any]:
        """Try to add a badge to a user's profile.

        Returns a dict with result info. This function is a template — adapt endpoint.
        """
        # Placeholder endpoint — replace with actual Gift Up endpoint
        endpoint = f"{self.api_base}/profiles/{username}/badges"
        payload = {"badge": badge_name}

        if dry_run or not self.token:
            logger.info(f"DRY RUN: POST {endpoint} payload={payload}")
            return {"dry_run": True, "endpoint": endpoint, "payload": payload}

        try:
            resp = requests.post(endpoint, json=payload, headers=self._headers(), timeout=10)
            resp.raise_for_status()
            logger.info(f"Badge added to {username}: {badge_name}")
            return {"status": "ok", "response": resp.json()}
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {"status": "error", "error": str(e), "status_code": getattr(e.response, 'status_code', None)}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GiftUp API client (template)")
    parser.add_argument("username", help="username to add badge to")
    parser.add_argument("badge", help="badge name, e.g. '🔥' or 'Verified'")
    parser.add_argument("--dry", action="store_true", help="dry run (no network)")
    args = parser.parse_args()

    client = GiftUpClient()
    result = client.add_badge_to_profile(args.username, args.badge, dry_run=args.dry)
    print(result)
