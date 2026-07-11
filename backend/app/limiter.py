"""
Shared SlowAPI rate limiter instance.
Importing from here ensures all routers share the same limiter,
so disabling it in tests (via app.state.limiter.enabled = False) works globally.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
