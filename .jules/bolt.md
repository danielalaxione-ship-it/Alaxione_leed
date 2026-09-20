## 2024-05-23 - [Dynamic waits in Google Maps scraping]
**Learning:** Replacing static wait_for_timeout(1500) with dynamic wait_for_selector('h1.DUwDvf') per lead significantly reduced execution time. Playwright's wait_for_selector with state='attached' safely avoids unnecessary waiting.
**Action:** Always prefer dynamic wait_for_selector over static timeouts when scraping iterative lists of pages.
