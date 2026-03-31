"""TofuPilot SDK version information."""

import importlib.metadata

__title__: str = "tofupilot.v2"
__version__: str = "0.7.12"
__openapi_doc_version__: str = "2.0.0"
__gen_version__: str = "1.0.0"
__user_agent__: str = f"tofupilot-sdk/python {__version__} {__gen_version__} {__openapi_doc_version__} tofupilot.v2"

try:
    if __package__ is not None:
        __version__ = importlib.metadata.version(__package__)
except importlib.metadata.PackageNotFoundError:
    pass
