## 2024-05-24 - Streamlit Subprocess Caching
**Learning:** Running synchronous subprocess calls (like `playwright install chromium`) directly inside a Streamlit action handler block blocks the main thread on every UI interaction (e.g., search submissions).
**Action:** Use `@st.cache_resource` on a wrapper function for one-time initialization setups (like downloading browser binaries) to ensure they only run once per application lifecycle, preventing redundant blocking delays on subsequent interactions.
