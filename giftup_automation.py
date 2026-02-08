# -*- coding: utf-8 -*-
"""
Browser automation template using Playwright (synchronous API).

This script logs in to Gift Up (web UI) and tries to add a badge/icon to the user's profile.

Requirements:
- `pip install playwright` and run `playwright install` locally.
- Set env vars `GIFTUP_EMAIL` and `GIFTUP_PASSWORD` or run interactively.

NOTE: The selectors and navigation are placeholders — inspect Gift Up UI and adapt.
"""

import os
import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EMAIL = os.getenv('GIFTUP_EMAIL')
PASSWORD = os.getenv('GIFTUP_PASSWORD')


def run_add_badge(email: str, password: str, badge_text: str = '🔥'):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1) ไปที่หน้าเข้าสู่ระบบ
        page.goto('https://giftup.co/login')
        logger.info('Opened login page')

        # NOTE: Adjust selectors below according to actual UI
        page.fill('input[name="email"]', email)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')
        logger.info('Logged in (assumed)')

        # 2) ไปที่หน้าโปรไฟล์ (placeholder URL)
        page.goto('https://giftup.co/account/profile')
        page.wait_for_load_state('networkidle')

        # 3) หาช่องใส่ bio หรือ badge แล้วอัปเดต
        try:
            # Example: fill a textarea called bio
            if page.query_selector('textarea[name="bio"]'):
                bio = page.input_value('textarea[name="bio"]')
                new_bio = f"{bio}\n{badge_text}"
                page.fill('textarea[name="bio"]', new_bio)
                page.click('button:has-text("Save")')
                page.wait_for_load_state('networkidle')
                logger.info('Badge added to bio and saved')
            else:
                logger.warning('Bio textarea not found; manual update may be required')

        except Exception as e:
            logger.error(f'Error updating profile: {e}')

        browser.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='GiftUp browser automation (template)')
    parser.add_argument('--badge', default='🔥', help='Badge text to add')
    parser.add_argument('--headless', action='store_true', help='Run headless')
    args = parser.parse_args()

    if not EMAIL or not PASSWORD:
        print('Set GIFTUP_EMAIL and GIFTUP_PASSWORD environment variables before running.')
    else:
        run_add_badge(EMAIL, PASSWORD, badge_text=args.badge)
