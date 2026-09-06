## 2024-09-06 - Replaced Static Waits with Dynamic Waits
**Learning:** Static sleeps (`wait_for_timeout`) in scraping loops are a massive performance bottleneck. The time compounded over a list of items completely dominates execution time. In this case, 3s per scrape added >75s for 25 items.
**Action:** Always replace `wait_for_timeout` with `locator.wait_for()` or `page.wait_for_selector()` when waiting for specific elements to load.
