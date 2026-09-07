## 2024-05-24 - Replaced static sleep with dynamic wait in Playwright scraper
**Learning:** Static waits (`wait_for_timeout`) in scraping loops scale poorly with the number of pages scraped (O(N) penalty). Using dynamic waits like `wait_for_selector` eliminates this delay when pages load faster than the static limit.
**Action:** Always favor dynamic locators (`wait_for_selector`) instead of static timeouts (`wait_for_timeout`) to improve Playwright script performance, especially in loops over multiple items.
