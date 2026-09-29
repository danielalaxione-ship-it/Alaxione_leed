## 2023-10-25 - Cache Streamlit setup tasks
**Learning:** Synchronous subprocess calls (like `playwright install`) in Streamlit run repeatedly on every UI interaction, blocking the main thread and slowing down the UI.
**Action:** Use `@st.cache_resource` to wrap synchronous setup calls that only need to run once per application lifecycle.
