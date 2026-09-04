## 2024-05-30 - Wait implicitly instead of statically in Playwright
**Learning:** Hardcoded timeouts (`page.wait_for_timeout(3000)`) in scraper scripts are slow and fragile. Waiting for a condition (e.g., node presence or count change) speeds up the execution by multiple times as it moves forward as soon as the condition is met, without waiting for the full timeout. Playwright's `wait_for_function` can evaluate arbitrary DOM state.
**Action:** Replace `page.wait_for_timeout()` with `page.wait_for_function()` or locator waits.
