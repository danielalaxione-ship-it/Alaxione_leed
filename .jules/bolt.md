## 2024-05-15 - Streamlit Subprocess Caching
**Learning:** Synchronous subprocess calls (like `playwright install chromium`) inside Streamlit form submission blocks block the main thread on every interaction, even if they only need to run once per application lifecycle.
**Action:** Always wrap application-level setup commands in `@st.cache_resource` to ensure they execute only once, preventing redundant thread blocking and improving UI responsiveness.
