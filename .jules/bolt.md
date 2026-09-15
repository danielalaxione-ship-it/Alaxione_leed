## 2024-05-19 - Replacing sequential dynamic waits with a single safe dynamic wait for Playwright Playwright

**Learning:** Playwright `page.wait_for_selector()` performs extensive layout and visibility checks under the hood. In `scraper.py`, replacing a static 3-second wait with a dynamic wait for `h1.DUwDvf` significantly improved performance (by ~40% for 26 leads). However, when querying multiple elements sequentially, chaining `wait_for_selector` or implicit visibility checks like `inner_text()` causes massive delays due to repeated layout recalculations on a complex DOM (like Google Maps).

**Action:** When migrating from static waits, use dynamic wait for the *primary* load signal (e.g., the title attaching to the DOM) using `state='attached'` to skip visibility checks. For subsequent elements, prefer `locator.count()` paired with `locator.text_content()` rather than `locator.inner_text()` to avoid triggering expensive, slow visibility checks.
