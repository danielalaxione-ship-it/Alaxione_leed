## 2024-09-28 - Cache Playwright installation in Streamlit
**Learning:** Synchronous subprocess calls (like `playwright install chromium`) in Streamlit block the main thread and re-run on every UI interaction if not cached. This adds unnecessary delay (e.g., ~5 seconds) to repeated operations.
**Action:** Use the `@st.cache_resource` decorator to wrap such subprocess calls, ensuring they only run once per application lifecycle and preventing redundant executions.
