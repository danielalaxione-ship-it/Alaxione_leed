## 2024-05-24 - Cache Streamlit subprocess calls
**Learning:** Running subprocess calls like `playwright install chromium` inline during Streamlit UI interactions redundantly executes on every interaction, blocking the main thread and causing significant latency (~5s delay each time).
**Action:** Use Streamlit's `@st.cache_resource` decorator to wrap synchronous subprocess installations so they only execute once per application lifecycle.
