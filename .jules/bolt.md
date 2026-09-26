## 2024-05-24 - Streamlit Synchronous Subprocess Blocking
**Learning:** Running `subprocess.run` directly inside a Streamlit UI interaction loop (like a form submission check) blocks the main thread on every interaction, even for idempotent operations like checking if Playwright browsers are installed.
**Action:** Use Streamlit's `@st.cache_resource` decorator on functions containing synchronous setup subprocesses so they only execute once per application lifecycle, preventing redundant executions and thread blocking on repeated UI interactions.
