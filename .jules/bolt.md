## 2024-05-24 - Bare except clauses catch SystemExit and KeyboardInterrupt
**Learning:** In Python, a bare `except:` catches all exceptions that inherit from `BaseException`, including `KeyboardInterrupt` and `SystemExit`. This can prevent users from forcefully stopping a script via Ctrl+C.
**Action:** When wrapping Playwright element waits (or other operations) in try-except blocks, always use `except Exception:` instead of a bare `except:` to ensure the program handles termination signals appropriately.
