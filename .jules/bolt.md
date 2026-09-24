## 2024-09-24 - Streamlit Main Thread Blocking
**Learning:** Running synchronous `subprocess.run` calls (like `playwright install`) directly in a Streamlit script's execution path blocks the main UI thread on every re-render/interaction, even if the dependency is already satisfied. This causes significant, redundant delays for users performing multiple searches.
**Action:** Use Streamlit's `@st.cache_resource` decorator to wrap expensive initialization/setup calls so they are only executed once per application lifecycle, keeping subsequent interactions fast and responsive.
