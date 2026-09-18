## 2023-10-24 - Static Sleep Bottleneck in Playwright Loop
**Learning:** In scraping loops processing multiple URLs, static `wait_for_timeout()` calls compound linearly, creating severe performance bottlenecks. For a list of 20 places, a static wait of 1.5s adds an unnecessary base delay of 30s.
**Action:** Always replace `wait_for_timeout()` inside iteration blocks with dynamic `wait_for_selector()` calls targeting the primary load-bearing element (e.g., page title or main data container).
