import os
import functools
import traceback
from typing import Optional, Dict, Any, Callable, TypeVar
import posthog
from .telemetry_config import is_telemetry_enabled

if is_telemetry_enabled():
    posthog.api_key = 'phc_egOxs66B4Dfq65Z53Et7wWc3demju3Lrz2pIrnBpwg9'
    posthog.host = 'https://us.i.posthog.com'
    posthog.debug = False
else:
    posthog.disabled = True

class ApiVersionWarning(Exception):
    """Not intended to be raised, instead used for posthog"""
    pass

class ApiV1Error(Exception):
    pass
