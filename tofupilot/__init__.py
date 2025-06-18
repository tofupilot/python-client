"""TofuPilot API client library."""

# Try to import the enhanced client first, fallback to auto-generated client if dependencies missing
try:
    from .client import TofuPilotClient
    _enhanced_client_available = True
except ImportError:
    # Fallback to auto-generated client if enhanced client dependencies are missing
    from .openapi_client import TofuPilotClient
    _enhanced_client_available = False

# Import the auto-generated client for advanced users
from .openapi_client import TofuPilotClient as OpenAPIClient

# Try to import models for convenience, but don't fail if they're not available
try:
    from .models import MeasurementOutcome, PhaseOutcome, SubUnit, UnitUnderTest, Step, Phase, Log
    _models_available = True
    model_exports = ["MeasurementOutcome", "PhaseOutcome", "SubUnit", "UnitUnderTest", "Step", "Phase", "Log"]
except ImportError:
    _models_available = False
    model_exports = []

# Try to import OpenHTF integration, but don't fail if OpenHTF dependencies are missing
try:
    from . import openhtf
    _openhtf_available = True
    openhtf_exports = ["openhtf"]
except ImportError:
    _openhtf_available = False
    openhtf_exports = []

# Try to import plugin functionality (pytest integration), but don't fail if pytest not available
try:
    from .plugin import numeric_step, string_step, conf
    _plugin_available = True
    plugin_exports = ["numeric_step", "string_step", "conf"]
except ImportError:
    _plugin_available = False
    plugin_exports = []

__version__ = "0.67.0.dev713"
__all__ = ["TofuPilotClient", "OpenAPIClient"] + model_exports + openhtf_exports + plugin_exports

# Inform users about available features
if not _enhanced_client_available:
    import warnings
    warnings.warn(
        "Enhanced TofuPilot client features (file attachments, logging) are not available. "
        "Install additional dependencies with: pip install requests certifi",
        ImportWarning,
        stacklevel=2
    )
