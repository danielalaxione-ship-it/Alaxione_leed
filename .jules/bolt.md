## 2023-10-24 - Playwright Static vs Dynamic Wait Botteneck
**Learning:** In a scraping loop, a static `page.wait_for_timeout` applied to every page linearly degrades performance. In Playwright, static waits accumulate directly into total execution time.
**Action:** Replace `wait_for_timeout` with `wait_for_selector(..., state='attached')` within a try-except block to dynamically advance as soon as the target element is loaded, reducing baseline delays significantly per loop iteration.
