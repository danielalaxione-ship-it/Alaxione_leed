## 2024-09-14 - Playwright Static Waits and Visibility Checks
**Learning:** Playwright `.inner_text()` forces expensive synchronous browser layout recalculations to check for element visibility. Additionally, static `wait_for_timeout` calls accumulate massive delays inside loops when iterating over multiple pages.
**Action:** Always prefer `.text_content()` over `.inner_text()` when CSS layout verification is unnecessary. Replace static timeouts with `wait_for_selector(..., state='attached')` to allow the script to proceed immediately upon DOM readiness.
