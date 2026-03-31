# Import the error tracking enhanced client by default
from .client_with_error_tracking import TofuPilotWithErrorTracking as TofuPilot
# Still export the base SDK for those who want it
from .sdk import TofuPilot as TofuPilotBase
from .sdkconfiguration import *

from ._version import (
    __title__,
    __version__,
    __openapi_doc_version__,
    __gen_version__,
    __user_agent__,
)

VERSION: str = __version__
OPENAPI_DOC_VERSION = __openapi_doc_version__
GENERATOR_VERSION = __gen_version__
USER_AGENT = __user_agent__

__all__ = [
    "TofuPilot",
    "TofuPilotBase",
    "VERSION",
    "OPENAPI_DOC_VERSION",
    "GENERATOR_VERSION",
    "USER_AGENT",
]
