"""TofuPilot SDK Runtime. DO NOT EDIT — maintained in clients/generator/runtime/."""

class NoResponseError(Exception):
    """Error raised when no HTTP response is received from the server."""

    message: str

    def __init__(self, message: str = "No response received"):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message
