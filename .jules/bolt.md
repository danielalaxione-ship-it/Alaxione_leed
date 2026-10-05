## 2024-10-05 - Cache Streamlit subprocess calls
**Learning:** In Streamlit, running expensive synchronous operations like `subprocess.run` directly in the execution flow (e.g., inside form submissions) causes significant UI blocking and redundant executions because Streamlit reruns the entire script on every interaction.
**Action:** Use `@st.cache_resource` for operations like dependency installation (`playwright install chromium`) that only need to run once per application lifecycle, avoiding repeated execution penalties on each search.
