## 2026-09-27 - Streamlit Subprocess Caching
**Learning:** In Streamlit applications, synchronous subprocess calls placed directly in the main execution flow (like `playwright install`) run every time a user interacts with the UI, blocking the main thread and causing severe perceived latency on repeated actions.
**Action:** Always wrap heavy synchronous initialization commands (that only need to run once per app lifecycle) in functions decorated with `@st.cache_resource` before calling them in the UI flow.
