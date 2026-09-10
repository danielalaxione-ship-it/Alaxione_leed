## 2024-09-10 - Playwright Scraping Performance Overheads & Race Conditions

**Learning:** Playwright's `inner_text()` includes implicit visibility checks that cause significant overhead during DOM reads. However, replacing global static waits (`wait_for_timeout`) with dynamic optional locators (e.g., waiting for ratings or phone numbers to attach) causes severe performance degradations due to sequential timeouts when those elements are naturally missing. Furthermore, synchronous checks like `.count()` on optional elements create race conditions if the preceding wait only targets a single unrelated element (like an `h1`).

**Action:** Prefer `text_content()` over `inner_text()` to bypass visibility checks for safe, pure micro-optimizations. When dealing with scraping pages with many optional fields, retain global timeouts or use `wait_for_load_state` if available, rather than applying individual targeted timeout waits that sequentially penalize pages missing data.
